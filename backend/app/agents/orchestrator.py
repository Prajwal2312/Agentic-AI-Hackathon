"""
Multi-Agent Orchestrator using LangGraph.
Coordinates:
1. Planning Phase (Autonomous Task Planner)
2. Discovery Agent (Extracts text, metadata, tables)
3. Context Intelligence Agent (Distinguishes PII vs Non-Personal Identifiers)
4. Context Verification Node (Conditional Edge for low confidence / ambiguous candidates)
5. Risk Assessment Agent (Calculates risk scores 0-100 and categories)
6. DPDP Compliance Agent (Maps findings to statutory provisions & rules)
7. Remediation Agent (Generates masked copies & approval queue)
8. Finalization & Audit Logging
"""

import time
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from backend.app.agents.state import AgentState
from backend.app.agents.discovery_agent import DiscoveryAgent
from backend.app.agents.context_agent import ContextAgent
from backend.app.agents.risk_agent import RiskAgent
from backend.app.agents.compliance_agent import ComplianceAgent
from backend.app.agents.remediation_agent import RemediationAgent

logger = logging.getLogger(__name__)

# Agent Instances
discovery_agent = DiscoveryAgent()
context_agent = ContextAgent()
risk_agent = RiskAgent()
compliance_agent = ComplianceAgent()
remediation_agent = RemediationAgent()

def planner_node(state: AgentState) -> Dict[str, Any]:
    """Autonomous Task Planning Node."""
    plan = [
        "1. Document Discovery: Scan authorized files, extract text and structural tables.",
        "2. Context Intelligence: Differentiate true PII from misleading numerical patterns (e.g. Order ID vs Phone).",
        "3. Verification Gate: Conditionally inspect ambiguous items using deep contextual cues or LLM.",
        "4. Risk Assessment: Quantify sensitivity, exposure, and aggregation risk on a 0-100 scale.",
        "5. DPDP Compliance Mapping: Align findings with India's DPDP Act 2023 & Rules 2025.",
        "6. Remediation Formulation: Generate redacted files and present approval actions for human oversight."
    ]
    return {
        "current_phase": "DISCOVERY",
        "task_plan": plan,
        "audit_logs": [{
            "agent_name": "Orchestrator Agent",
            "action": "PLAN_INITIALIZED",
            "details": f"Autonomous audit execution plan generated with 6 phases for session {state.session_id}."
        }],
        "agent_executions": {
            "Orchestrator Agent": {
                "status": "COMPLETED",
                "task_description": "Formulated autonomous multi-agent audit plan with conditional decision boundaries.",
                "execution_duration_ms": 15,
                "findings_count": 6,
                "logs": [f"Session {state.session_id} planned successfully."]
            }
        }
    }

def discovery_node(state: AgentState) -> Dict[str, Any]:
    return discovery_agent.run(state)

def context_node(state: AgentState) -> Dict[str, Any]:
    return context_agent.run(state)

def verification_gate(state: AgentState) -> Literal["extra_verification", "risk_node"]:
    """Conditional Edge: routes to extra verification if ambiguous candidates exist."""
    if state.needs_extra_verification and len(state.ambiguous_candidates) > 0:
        return "extra_verification"
    return "risk_node"

def extra_verification_node(state: AgentState) -> Dict[str, Any]:
    """Deep verification pass for ambiguous candidates."""
    logs = [f"Deep verification triggered for {len(state.ambiguous_candidates)} ambiguous candidates."]
    updated_findings = []
    
    for f in state.findings:
        if f.is_ambiguous:
            # Perform second-order verification based on file-level contextual hints
            # If the file contains customer names and phone numbers, an ambiguous 10-digit number
            # with non-standard header is tagged as LIKELY_PERSONAL_DATA with review tag
            has_other_customer_data = any(
                other.classification == "CONFIRMED_PERSONAL_DATA" and other.file_name == f.file_name
                for other in state.findings
            )
            if has_other_customer_data and f.raw_value.isdigit() and len(f.raw_value) == 10 and f.raw_value[0] in "6789":
                f.classification = "LIKELY_PERSONAL_DATA"
                f.confidence = 0.78
                f.explanation += " (Resolved during verification: Co-located with verified customer records)."
                f.is_ambiguous = False
                logs.append(f"Ambiguous candidate in {f.file_name} resolved to LIKELY_PERSONAL_DATA via co-location analysis.")
            else:
                f.explanation += " (Maintained AMBIGUOUS after verification: Lacks conclusive semantic context. Awaiting human confirmation)."
                logs.append(f"Ambiguous candidate in {f.file_name} preserved for human review.")
        updated_findings.append(f)

    return {
        "current_phase": "RISK_ASSESSMENT",
        "findings": updated_findings,
        "needs_extra_verification": False,
        "audit_logs": [{
            "agent_name": "Context Intelligence Agent (Deep Verification)",
            "action": "AMBIGUOUS_VERIFICATION_COMPLETED",
            "details": f"Processed {len(state.ambiguous_candidates)} ambiguous items through contextual co-location verification."
        }]
    }

def risk_node(state: AgentState) -> Dict[str, Any]:
    return risk_agent.run(state)

def compliance_node(state: AgentState) -> Dict[str, Any]:
    return compliance_agent.run(state)

def remediation_node(state: AgentState) -> Dict[str, Any]:
    return remediation_agent.run(state)

def build_orchestrator_graph():
    """Builds and compiles the LangGraph StateGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("context", context_node)
    workflow.add_node("extra_verification", extra_verification_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("remediation", remediation_node)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Linear and conditional transitions
    workflow.add_edge("planner", "discovery")
    workflow.add_edge("discovery", "context")
    
    # Conditional Edge: Context -> Verification Gate -> (extra_verification OR risk)
    workflow.add_conditional_edges(
        "context",
        verification_gate,
        {
            "extra_verification": "extra_verification",
            "risk_node": "risk"
        }
    )
    workflow.add_edge("extra_verification", "risk")
    workflow.add_edge("risk", "compliance")
    workflow.add_edge("compliance", "remediation")
    workflow.add_edge("remediation", END)

    app = workflow.compile()
    return app

# Singleton compiled LangGraph application
orchestrator_app = build_orchestrator_graph()
