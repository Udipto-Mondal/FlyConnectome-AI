"""
Planner Agent for FlyConnectome AI.
Parses natural language research queries into structured biological circuit specifications,
identifies candidate sensory/motor neuropils, and plans graph traversal constraints.
"""

from typing import Dict, List, Any, Optional
import re
from ..config import settings
from ..graph.engine import graph_engine
from ..graph.connectome_data import SHOWCASE_PRESETS


class PlannerAgent:
    def __init__(self):
        self.name = "Query Planning & Circuit Hypothesis Agent"

    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query and return a structured plan for the Graph-RAG agent.
        """
        q = user_query.lower()
        thought_steps = []
        thought_steps.append(f"Received query: '{user_query}'")

        # 1. Check for match with curated showcase presets
        matched_preset = None
        for preset in SHOWCASE_PRESETS:
            if preset["id"].lower() in q or any(kw in q for kw in [preset["subsystem"].lower(), preset["title"].lower()]):
                matched_preset = preset
                break

        # 2. Extract circuit goal / subsystem
        subsystem = "General Circuit"
        sources = []
        targets = []
        ablation_targets = []
        circuit_goal = "Investigate synaptic connectivity"

        if "escape" in q or "jump" in q or "looming" in q or "shadow" in q or "threat" in q or "giant fiber" in q:
            subsystem = "Visual Escape Reflex"
            circuit_goal = "Map high-velocity looming stimulus to emergency leg-jump & flight motor response"
            sources = ["10001", "10002", "10003", "10005", "10006"]  # R1-R6, L1, L2, LC4, LPLC2
            targets = ["20145", "20146"]  # TTMn, DLMn
            thought_steps.append("Classified intent as: Visual Looming & Emergency Takeoff Circuit.")
            thought_steps.append("Identified candidate sensory inputs: Photoreceptors (R1-R6), Lamina (L1/L2), Lobula Columnar (LC4/LPLC2).")
            thought_steps.append("Identified candidate motor outputs: Jump Motor (TTMn) & Wing Motor (DLMn).")

        elif "compass" in q or "navigation" in q or "heading" in q or "sun" in q or "steering" in q or "ellipsoid" in q or "e-pg" in q:
            subsystem = "Sun Compass & Spatial Navigation"
            circuit_goal = "Trace polarized sky light and celestial landmarks to central compass heading and steering motor output"
            sources = ["30010", "30011"]  # Me-Tu, TuBu01
            targets = ["30017", "30018"]  # PFL3, DNb01
            thought_steps.append("Classified intent as: Central Complex Navigation & Compass Steering.")
            thought_steps.append("Identified candidate sensory inputs: Anterior Optic Tubercle (Me-Tu, TuBu01).")
            thought_steps.append("Identified candidate motor outputs: Steering Pre-Motor (PFL3) and Descending Steering Motor (DNb01).")

        elif "courtship" in q or "male" in q or "p1" in q or "song" in q or "mating" in q or "dimorphic" in q:
            subsystem = "Sex-Dimorphic Courtship Circuit"
            circuit_goal = "Investigate 2026 Male Connectome sex-dimorphic circuitry from female contact pheromone to P1 command and wing vibration song"
            sources = ["50001", "50002"]  # Sensory_ppk23, vPN1
            targets = ["50004", "50005"]  # pIP10, dPR1
            thought_steps.append("Classified intent as: Sex-Dimorphic Male Courtship & Song Generation.")
            thought_steps.append("Identified candidate sensory inputs: Foreleg Pheromone Sensor (ppk23), vPN1.")
            thought_steps.append("Identified candidate motor outputs: Descending Song Command (pIP10) and Wing Motor Pre-motor (dPR1).")

        elif "odor" in q or "olfactory" in q or "smell" in q or "mushroom" in q or "memory" in q or "valence" in q:
            subsystem = "Olfactory Associative Learning"
            circuit_goal = "Trace odor sensory inputs through antennal projection neurons and Kenyon cells to MBON valence decision"
            sources = ["40001", "40002"]  # ORN_Or42b, PN_DM1
            targets = ["40005", "40006"]  # MBON_alpha3, DNg02
            thought_steps.append("Classified intent as: Olfactory Valence & Associative Memory Circuit.")
            thought_steps.append("Identified candidate sensory inputs: Antennal Receptor (Or42b) and Projection Neuron (PN_DM1).")
            thought_steps.append("Identified candidate motor outputs: MBON_alpha3 valence readout and DNg02 locomotor driver.")

        else:
            # General keyword / entity matching
            found_neurons = graph_engine.search_neurons(q)
            if found_neurons:
                sources = [str(found_neurons[0]["id"])]
                if len(found_neurons) > 1:
                    targets = [str(found_neurons[1]["id"])]
                else:
                    targets = ["20145", "20146"]
                thought_steps.append(f"Identified entity query mentioning: {[n['name'] for n in found_neurons[:3]]}.")
            else:
                # Default to visual escape
                subsystem = "Visual Escape Reflex"
                sources = ["10005"]
                targets = ["20145"]
                thought_steps.append("Defaulted to canonical Drosophila Escape circuit for exploration.")

        # 3. Check for ablation / knockout requests
        is_ablation_requested = any(kw in q for kw in [
            "knockout", "knock out", "knocked out", "ablate", "ablation", "ablated",
            "silence", "silenced", "silencing", "destroy", "destroyed", "sever", "severed",
            "remove", "removed", "what happens if", "what if"
        ])
        if is_ablation_requested:
            thought_steps.append("Detected in-silico neuronal ablation request.")
            # Search for which neuron to silence
            if "giant fiber" in q or "gf" in q:
                ablation_targets = ["10234"]
                thought_steps.append("Targeting Giant Fiber (GF_L, ID: 10234) for simulated knockout.")
            elif "e-pg" in q or "compass" in q:
                ablation_targets = ["30013"]
                thought_steps.append("Targeting E-PG Compass Neuron (ID: 30013) for simulated knockout.")
            elif "p1" in q:
                ablation_targets = ["50003"]
                thought_steps.append("Targeting P1 Master Command Neuron (ID: 50003) for simulated knockout.")
            elif "kc" in q or "kenyon" in q:
                ablation_targets = ["40003"]
                thought_steps.append("Targeting Kenyon Cell (KC_gamma, ID: 40003) for simulated knockout.")
            else:
                # Default to key relay for that subsystem
                if subsystem == "Visual Escape Reflex":
                    ablation_targets = ["10234"]
                elif subsystem == "Sun Compass & Spatial Navigation":
                    ablation_targets = ["30013"]
                elif subsystem == "Sex-Dimorphic Courtship Circuit":
                    ablation_targets = ["50003"]
                else:
                    ablation_targets = ["40003"]
                thought_steps.append(f"Auto-selected key bottleneck neuron (ID: {ablation_targets[0]}) for ablation study.")

        plan_result = {
            "subsystem": subsystem,
            "circuit_goal": circuit_goal,
            "source_neuron_ids": sources,
            "target_neuron_ids": targets,
            "is_ablation_requested": is_ablation_requested,
            "ablation_target_ids": ablation_targets,
            "thought_log": thought_steps
        }

        return plan_result


planner_agent = PlannerAgent()
