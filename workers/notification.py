#!/usr/bin/env python3
"""
MEOK AI Labs - Notification Service
Send alerts via email, Slack, SMS, etc.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    type: NotificationType
    recipient: str
    subject: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    metadata: Dict[str, Any] = None


class NotificationChannel(ABC):
    """Abstract notification channel"""

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send notification"""
        pass

    @abstractmethod
    async def test(self) -> bool:
        """Test channel connectivity"""
        pass


class EmailChannel(NotificationChannel):
    """Email notification channel"""

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = 587,
        username: str = None,
        password: str = None,
        from_addr: str = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_addr = from_addr or os.getenv("SMTP_FROM", "alerts@meok.ai")

    async def send(self, notification: Notification) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = notification.subject
            msg["From"] = self.from_addr
            msg["To"] = notification.recipient

            text_part = MIMEText(notification.message, "plain")
            html_part = MIMEText(self._format_html(notification), "html")

            msg.attach(text_part)
            msg.attach(html_part)

            await asyncio.to_thread(self._send_smtp, msg, notification.recipient)

            logger.info(f"Email sent to {notification.recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _send_smtp(self, msg, to_addr: str) -> None:
        """Send via SMTP (blocking)"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.sendmail(self.from_addr, to_addr, msg.as_string())

    def _format_html(self, notification: Notification) -> str:
        """Format HTML email body"""
        priority_colors = {
            "low": "#36a64f",
            "medium": "#ff9900",
            "high": "#ff6600",
            "critical": "#ff0000",
        }

        color = priority_colors.get(notification.priority, "#ff9900")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 15px; }}
                .content {{ padding: 20px; background: #f5f5f5; }}
                .footer {{ padding: 10px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>MEOK AI Labs Alert</h2>
            </div>
            <div class="content">
                <h3>{notification.subject}</h3>
                <p>{notification.message}</p>
            </div>
            <div class="footer">
                MEOK AI Labs Monitoring System
            </div>
        </body>
        </html>
        """

    async def test(self) -> bool:
        """Test SMTP connection"""
        try:
            await asyncio.to_thread(smtplib.SMTP, self.smtp_host, self.smtp_port)
            return True
        except Exception:
            return False


class SlackChannel(NotificationChannel):
    """Slack notification channel"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    async def send(self, notification: Notification) -> bool:
        """Send Slack notification"""
        import httpx

        priority_emojis = {
            "low": ":large_green_circle:",
            "medium": ":large_yellow_circle:",
            "high": ":large_orange_circle:",
            "critical": ":red_circle:",
        }

        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{priority_emojis.get(notification.priority, ':large_yellow_circle:')} {notification.subject}",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": notification.message},
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Sent from MEOK AI Labs | Priority: {notification.priority.upper()}",
                        }
                    ],
                },
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload, timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False

    async def test(self) -> bool:
        """Test Slack webhook"""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={"text": "MEOK AI Labs test message"},
                    timeout=10,
                )
                return response.status_code == 200
        except Exception:
            return False


class WebhookChannel(NotificationChannel):
    """Generic webhook notification"""

    def __init__(self, webhook_url: str = None, secret: str = None):
        self.webhook_url = webhook_url
        self.secret = secret or os.getenv("WEBHOOK_SECRET")

    async def send(self, notification: Notification) -> bool:
        """Send webhook notification"""
        import httpx
        import hashlib
        import hmac
        import json
        import time

        payload = {
            "type": notification.type,
            "subject": notification.subject,
            "message": notification.message,
            "priority": notification.priority,
            "metadata": notification.metadata or {},
            "timestamp": asyncio.get_event_loop().time(),
        }

        headers = {"Content-Type": "application/json"}

        if self.secret:
            body = json.dumps(payload)
            signature = hmac.new(
                self.secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Meok-Signature"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url, json=payload, headers=headers, timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False

    async def test(self) -> bool:
        """Test webhook"""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url, json={"test": True}, timeout=10
                )
                return response.status_code == 200
        except Exception:
            return False


class NotificationService:
    """Main notification service"""

    def __init__(self):
        self.channels: Dict[NotificationType, NotificationChannel] = {}
        self._setup_default_channels()

    def _setup_default_channels(self) -> None:
        """Set up default channels"""
        if os.getenv("SMTP_HOST"):
            self.channels[NotificationType.EMAIL] = EmailChannel()

        if os.getenv("SLACK_WEBHOOK_URL"):
            self.channels[NotificationType.SLACK] = SlackChannel()

        if os.getenv("WEBHOOK_URL"):
            self.channels[NotificationType.WEBHOOK] = WebhookChannel()

    def add_channel(
        self, notification_type: NotificationType, channel: NotificationChannel
    ) -> None:
        """Add a notification channel"""
        self.channels[notification_type] = channel

    async def send(self, notification: Notification) -> Dict[str, bool]:
        """Send notification to all configured channels"""
        results = {}

        channel = self.channels.get(notification.type)
        if channel:
            results[notification.type] = await channel.send(notification)
        else:
            results[notification.type] = False
            logger.warning(f"No channel configured for {notification.type}")

        return results

    async def send_alert(
        self,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: List[NotificationType] = None,
        **metadata,
    ) -> Dict[str, Dict[str, bool]]:
        """Send alert to multiple channels"""
        channels = channels or list(self.channels.keys())
        results = {}

        for channel_type in channels:
            notification = Notification(
                type=channel_type,
                recipient="alert",
                subject=subject,
                message=message,
                priority=priority,
                metadata=metadata,
            )

            results[channel_type.value] = await self.send(notification)

        return results


async def main():
    """Test notification service"""
    service = NotificationService()

    await service.send_alert(
        subject="Test Alert",
        message="This is a test notification from MEOK AI Labs",
        priority=NotificationPriority.HIGH,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
