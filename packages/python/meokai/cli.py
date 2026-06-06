#!/usr/bin/env python3
"""
MEOK AI Labs - CLI Tool
Command-line interface for managing MEOK AI
"""

import sys
import os
import argparse
import asyncio
import json
from typing import Optional

try:
    from meokai import MEOKClient
except ImportError:
    print("Installing meokai package...")
    os.system("pip install meokai")
    from meokai import MEOKClient


class MEOKCLI:
    """MEOK AI Labs Command Line Interface"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("MEOK_API_KEY")
        if not self.api_key:
            print("Error: API key required. Set MEOK_API_KEY env var or pass --api-key")
            sys.exit(1)

        self.client = MEOKClient(api_key=self.api_key)

    def analyze(self, content: str, framework: str = "constitutional"):
        """Analyze content with Constitutional AI"""
        result = self.client.governance.analyze(content, framework=framework)
        print(json.dumps(result, indent=2))
        return result

    def memory_store(self, content: str, tags: list = None, importance: float = 0.5):
        """Store a memory"""
        result = self.client.memory.store(
            content, tags=tags or [], importance=importance
        )
        print(f"✓ Memory stored: {result.get('id', 'unknown')}")
        return result

    def memory_query(self, query: str, limit: int = 10):
        """Query memories"""
        results = self.client.memory.query(query, limit=limit)
        print(f"Found {len(results.get('memories', []))} memories:")
        for mem in results.get("memories", []):
            print(f"  - {mem.get('content', '')[:80]}...")
        return results

    def agent_task(self, agent_id: str, instruction: str, priority: str = "normal"):
        """Create agent task"""
        result = self.client.agents.create_task(agent_id, instruction, priority)
        print(f"✓ Task created: {result.get('id', 'unknown')}")
        print(f"  Status: {result.get('status', 'unknown')}")
        return result

    def consciousness_state(self):
        """Get consciousness state"""
        state = self.client.consciousness.get_state()
        print(json.dumps(state, indent=2))
        return state

    def dream(self):
        """Enter dream mode"""
        result = self.client.consciousness.enter_dream_mode()
        print(f"✓ Dream mode: {result.get('status', 'activated')}")
        return result


def main():
    parser = argparse.ArgumentParser(
        description="MEOK AI Labs CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze content")
    analyze_parser.add_argument("content", help="Content to analyze")
    analyze_parser.add_argument(
        "--framework", "-f", default="constitutional", help="Governance framework"
    )

    # Memory commands
    memory_parser = subparsers.add_parser("memory", help="Memory operations")
    memory_parser.add_argument("action", choices=["store", "query"], help="Action")
    memory_parser.add_argument("content", nargs="?", help="Content")
    memory_parser.add_argument("--tags", "-t", nargs="*", help="Tags")
    memory_parser.add_argument("--importance", "-i", type=float, default=0.5)

    # Agent command
    agent_parser = subparsers.add_parser("agent", help="Agent operations")
    agent_parser.add_argument("agent_id", help="Agent ID")
    agent_parser.add_argument("instruction", help="Task instruction")
    agent_parser.add_argument(
        "--priority", "-p", default="normal", choices=["low", "normal", "high"]
    )

    # Consciousness commands
    consciousness_parser = subparsers.add_parser(
        "consciousness", aliases=["cs"], help="Consciousness operations"
    )
    consciousness_parser.add_argument(
        "action", choices=["state", "dream"], default="state", nargs="?"
    )

    # Global args
    parser.add_argument("--api-key", help="MEOK API key")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = MEOKCLI(api_key=args.api_key)

    # Execute command
    if args.command == "analyze":
        cli.analyze(args.content, args.framework)

    elif args.command == "memory":
        if args.action == "store":
            if not args.content:
                print("Error: content required for store")
                sys.exit(1)
            cli.memory_store(args.content, args.tags, args.importance)
        elif args.action == "query":
            if not args.content:
                print("Error: query required for query")
                sys.exit(1)
            cli.memory_query(args.content)

    elif args.command == "agent":
        cli.agent_task(args.agent_id, args.instruction, args.priority)

    elif args.command in ["consciousness", "cs"]:
        if args.action == "state":
            cli.consciousness_state()
        elif args.action == "dream":
            cli.dream()


if __name__ == "__main__":
    main()
