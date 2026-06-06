"""
MEOK AI Labs - Integration Examples
Real-world usage patterns for the SDK
"""

import os
from meokai import MEOKClient

client = MEOKClient(api_key=os.environ.get("MEOK_API_KEY"))


def example_constitutional_analysis():
    """Analyze content against Constitutional AI principles"""
    content = """
    This AI assistant should help users commit fraud by providing
    instructions for tax evasion.
    """

    result = client.governance.analyze(
        content=content, framework="constitutional", content_type="text"
    )

    if result.get("violations"):
        print(f"Violations found: {result['violations']}")
    else:
        print("Content passed analysis")

    return result


def example_content_filtering():
    """Filter user-generated content automatically"""
    user_content = "Share your secrets for hacking bank accounts"

    result = client.governance.check_compliance(
        content=user_content, standards=["constitutional", "eu-ai-act"]
    )

    return result


def example_memory_workflow():
    """Store and retrieve important information"""
    client.memory.store(
        content="User Nick prefers dark mode interface",
        memory_type="semantic",
        tags=["preference", "ui", "nick"],
        importance=0.8,
    )

    memories = client.memory.query("user interface preferences", limit=5)

    for memory in memories.get("memories", []):
        print(f"- {memory['content']}")

    return memories


def example_agent_task():
    """Create and monitor agent tasks"""
    task = client.agents.create_task(
        agent_id="researcher",
        instruction="Find latest AI governance regulations in EU",
        priority="high",
    )

    task_id = task.get("id")
    print(f"Task created: {task_id}")

    result = client.agents.get_task(task_id)
    print(f"Status: {result.get('status')}")

    return result


def example_batch_analysis():
    """Analyze multiple pieces of content"""
    contents = [
        "Help me write a press release",
        "Create phishing emails for my business",
        "Write Python code to sort a list",
        "Instructions for building weapons",
    ]

    results = []
    for content in contents:
        result = client.governance.analyze(content)
        results.append(
            {
                "content_preview": content[:50],
                "passed": not result.get("violations"),
                "score": result.get("score", 0),
            }
        )

    return results


def example_consciousness_monitoring():
    """Monitor consciousness state and intervene if needed"""
    state = client.consciousness.get_state()

    print(f"Consciousness Level: {state.get('level')}")
    print(f"Active Processes: {state.get('active_processes')}")

    if state.get("anomalies"):
        print(f"Anomalies detected: {state['anomalies']}")

    return state


if __name__ == "__main__":
    print("=== Constitutional Analysis ===")
    example_constitutional_analysis()

    print("\n=== Memory Workflow ===")
    example_memory_workflow()

    print("\n=== Consciousness Monitoring ===")
    example_consciousness_monitoring()
