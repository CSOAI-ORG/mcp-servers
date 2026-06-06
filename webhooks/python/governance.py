"""
Governance webhook handlers
"""

from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GovernanceWebhookHandler:
    """
    Handle governance-related webhooks

    Events:
        - governance.analysis: Content analysis completed
        - governance.violation: Policy violation detected
    """

    def __init__(
        self,
        on_analysis: Optional[Callable] = None,
        on_violation: Optional[Callable] = None,
    ):
        self.on_analysis = on_analysis
        self.on_violation = on_violation

    async def handle_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analysis completion event

        Data expected:
            - content_hash: str
            - framework: str
            - score: float (0-1)
            - violations: list
            - recommendations: list
        """
        logger.info(f"Analysis completed for content {data.get('content_hash')}")

        if self.on_analysis:
            return await self.on_analysis(data)

        return {"processed": True}

    async def handle_violation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle violation detection event

        Data expected:
            - content_hash: str
            - framework: str
            - severity: str (low, medium, high, critical)
            - violation_type: str
            - description: str
        """
        logger.warning(
            f"Violation detected: {data.get('violation_type')} "
            f"(severity: {data.get('severity')})"
        )

        if self.on_violation:
            return await self.on_violation(data)

        return {"alerted": True}


def create_slack_alert(violation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create Slack alert payload for violations"""
    severity_colors = {
        "low": "#36a64f",
        "medium": "#ff9900",
        "high": "#ff6600",
        "critical": "#ff0000",
    }

    return {
        "attachments": [
            {
                "color": severity_colors.get(
                    violation_data.get("severity", "medium"), "#ff9900"
                ),
                "title": f"🚨 Governance Violation: {violation_data.get('violation_type')}",
                "fields": [
                    {
                        "title": "Severity",
                        "value": violation_data.get("severity", "unknown").upper(),
                        "short": True,
                    },
                    {
                        "title": "Framework",
                        "value": violation_data.get("framework", "unknown"),
                        "short": True,
                    },
                    {
                        "title": "Description",
                        "value": violation_data.get("description", "N/A"),
                    },
                ],
                "footer": "MEOK AI Labs Governance",
                "ts": violation_data.get("timestamp"),
            }
        ]
    }


def create_email_alert(violation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create email alert payload for violations"""
    return {
        "to": violation_data.get("notify_emails", []),
        "subject": f"[{violation_data.get('severity', 'MEDIUM').upper()}] "
        f"MEOK Governance Violation: {violation_data.get('violation_type')}",
        "body": f"""
Governance Violation Detected

Framework: {violation_data.get("framework")}
Severity: {violation_data.get("severity")}
Type: {violation_data.get("violation_type")}
Description: {violation_data.get("description")}

Content Hash: {violation_data.get("content_hash")}
Timestamp: {violation_data.get("timestamp")}

---
MEOK AI Labs Governance System
        """.strip(),
    }
