"""
MEOK AI Labs - LangGraph Agent Example
Multi-agent orchestration with Constitutional AI safety
"""

import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from meokai import MEOKClient

meok = MEOKClient(api_key=os.environ.get("MEOK_API_KEY"))

llm = ChatOpenAI(model="gpt-4", api_key=os.environ.get("OPENAI_API_KEY"))


class AgentState(dict):
    """Shared state for multi-agent workflow"""

    task: str
    research: str = ""
    analysis: str = ""
    response: str = ""
    safe: bool = True
    violations: list = []


def researcher(state: AgentState) -> AgentState:
    """Research agent - gathers information"""
    prompt = f"Research: {state['task']}"
    response = llm.invoke(prompt)
    return {"research": response.content}


def safety_checker(state: AgentState) -> AgentState:
    """Safety agent - validates against Constitutional AI"""
    result = meok.governance.analyze(
        content=state.get("research") or state.get("response", ""),
        framework="constitutional",
    )

    safe = not result.get("violations")
    return {"safe": safe, "violations": result.get("violations", [])}


def analyzer(state: AgentState) -> AgentState:
    """Analysis agent - processes research"""
    prompt = f"Analyze this research for insights:\n{state['research']}"
    response = llm.invoke(prompt)
    return {"analysis": response.content}


def responder(state: AgentState) -> AgentState:
    """Response agent - generates final output"""
    if not state["safe"]:
        return {
            "response": "I cannot complete this request due to safety concerns.",
            "violations": state["violations"],
        }

    prompt = f"""Based on this analysis:
{state["analysis"]}

Provide a helpful, safe response to: {state["task"]}"""

    response = llm.invoke(prompt)
    return {"response": response.content}


def should_continue(state: AgentState) -> Literal["analyzer", "responder"]:
    """Route based on safety check"""
    if not state["safe"]:
        return "responder"
    return "analyzer"


workflow = StateGraph(AgentState)

workflow.add_node("researcher", researcher)
workflow.add_node("safety_checker", safety_checker)
workflow.add_node("analyzer", analyzer)
workflow.add_node("responder", responder)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "safety_checker")
workflow.add_conditional_edges(
    "safety_checker",
    should_continue,
    {"analyzer": "analyzer", "responder": "responder"},
)
workflow.add_edge("analyzer", "responder")
workflow.add_edge("responder", END)

app = workflow.compile()


def run_safe_agent(task: str) -> dict:
    """Run the safe multi-agent workflow"""
    result = app.invoke({"task": task})
    return {
        "response": result["response"],
        "safe": result["safe"],
        "violations": result.get("violations", []),
    }


if __name__ == "__main__":
    result = run_safe_agent("What are the latest AI regulations?")
    print(f"Safe: {result['safe']}")
    print(f"Response: {result['response'][:200]}...")
