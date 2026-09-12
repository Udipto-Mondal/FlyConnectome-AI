"""
Multi-Agent Orchestrator for NeuroGraph AI.
Coordinates the Planner, Graph-RAG, Literature, and Synthesis agents into an autonomous discovery workflow.
"""

from typing import Dict, Any, List
import time
from .planner_agent import planner_agent
from .graph_rag_agent import graph_rag_agent
from .literature_agent import literature_agent
from .synthesis_agent import synthesis_agent


class AgentOrchestrator:
    def __init__(self):
        self.name = "NeuroGraph Multi-Agent Orchestrator"

    def run_discovery_pipeline(self, user_query: str) -> Dict[str, Any]:
        """
        Execute full end-to-end multi-agent circuit discovery pipeline.
        """
        start_time = time.time()
        agent_timeline: List[Dict[str, Any]] = []

        # 1. Planner Agent
        t0 = time.time()
        plan_result = planner_agent.plan(user_query)
        agent_timeline.append({
            "agent_id": "planner",
            "agent_name": planner_agent.name,
            "role": "Intent Classification & Neuropil Targeting",
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "logs": plan_result["thought_log"]
        })

        # 2. Graph-RAG Agent
        t0 = time.time()
        graph_result = graph_rag_agent.execute(plan_result)
        agent_timeline.append({
            "agent_id": "graph_rag",
            "agent_name": graph_rag_agent.name,
            "role": "Ground-Truth Connectome Traversal & Subgraph Extraction",
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "logs": graph_result["thought_log"]
        })

        # 3. Literature Validation Agent
        t0 = time.time()
        subsystem = plan_result["subsystem"]
        discovered_nodes = graph_result["subgraph"].get("nodes", [])
        lit_result = literature_agent.search_and_validate(subsystem, discovered_nodes)
        agent_timeline.append({
            "agent_id": "literature",
            "agent_name": literature_agent.name,
            "role": "Europe PMC & PubMed Peer-Reviewed Literature Grounding",
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "logs": lit_result["thought_log"]
        })

        # 4. Synthesis & Report Agent
        t0 = time.time()
        report_result = synthesis_agent.synthesize(
            user_query=user_query,
            plan=plan_result,
            graph_data=graph_result,
            literature_data=lit_result
        )
        agent_timeline.append({
            "agent_id": "synthesis",
            "agent_name": synthesis_agent.name,
            "role": "Scientific Discovery Report & Topology Compilation",
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "logs": report_result["thought_log"]
        })

        total_duration = round((time.time() - start_time) * 1000, 1)

        return {
            "query": user_query,
            "plan": plan_result,
            "graph": {
                "paths": graph_result["paths"],
                "subgraph": graph_result["subgraph"],
                "bottlenecks": graph_result["bottlenecks"],
                "sources": graph_result["sources"],
                "targets": graph_result["targets"],
                "total_pathways_found": graph_result["total_pathways_found"]
            },
            "ablation": graph_result.get("ablation"),
            "literature": lit_result["papers"],
            "report": report_result,
            "agent_timeline": agent_timeline,
            "execution_time_ms": total_duration
        }


orchestrator = AgentOrchestrator()
