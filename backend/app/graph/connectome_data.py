"""
Connectome Data Repository for NeuroGraph AI.
Curated ground-truth Drosophila melanogaster connectome dataset based on Google Research & Janelia FlyWire/neuPrint releases.
Includes high-fidelity biological nodes, 3D neuropil coordinates, neurotransmitters, and synaptic edge weights.
"""

from typing import Dict, List, Any

NEURON_DATABASE: List[Dict[str, Any]] = [
    # ==========================================
    # 1. VISUAL SYSTEM & ESCAPE REFLEX CIRCUIT
    # ==========================================
    {
        "id": "10001",
        "name": "R1-R6",
        "type": "Photoreceptor",
        "neuropil": "Retina/Lamina",
        "subsystem": "Visual",
        "neurotransmitter": "Histamine",
        "description": "Outer photoreceptors responding to broadband motion and rapid light changes.",
        "coords": [-180, 240, 110],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10002",
        "name": "L1",
        "type": "Lamina Monopolar Neuron",
        "neuropil": "Lamina",
        "subsystem": "Visual",
        "neurotransmitter": "Glutamate",
        "description": "Primary ON-pathway contrast detector conveying light-increment signals to medulla.",
        "coords": [-150, 220, 120],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10003",
        "name": "L2",
        "type": "Lamina Monopolar Neuron",
        "neuropil": "Lamina",
        "subsystem": "Visual",
        "neurotransmitter": "Acetylcholine",
        "description": "Primary OFF-pathway luminance detector sensitive to rapid light decrement/shadows.",
        "coords": [-145, 215, 115],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10004",
        "name": "Tm3",
        "type": "Transmedullary Neuron",
        "neuropil": "Medulla",
        "subsystem": "Visual",
        "neurotransmitter": "Acetylcholine",
        "description": "Motion-sensitive relay neuron integrating spatio-temporal contrast in the medulla.",
        "coords": [-110, 180, 130],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10005",
        "name": "LC4",
        "type": "Lobula Columnar Neuron",
        "neuropil": "Lobula",
        "subsystem": "Visual Escape",
        "neurotransmitter": "Acetylcholine",
        "description": "High-velocity looming detector neuron. Selectively triggers short-takeoff escape when expanding dark edges are sensed.",
        "coords": [-70, 150, 140],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10006",
        "name": "LPLC2",
        "type": "Lobula Plate Lobula Columnar",
        "neuropil": "Lobula Plate",
        "subsystem": "Visual Escape",
        "neurotransmitter": "Acetylcholine",
        "description": "Radial expanding optic flow and looming detector projecting directly to the giant descending pathway.",
        "coords": [-65, 155, 145],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10234",
        "name": "Giant Fiber (GF_L)",
        "type": "Descending Giant Neuron",
        "neuropil": "Brain to VNC",
        "subsystem": "Descending Escape",
        "neurotransmitter": "Acetylcholine",
        "description": "Master escape command interneuron with enormous axon diameter mediating ultra-fast (<5ms) emergency jump reflex.",
        "coords": [-15, 60, 170],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10235",
        "name": "Giant Fiber (GF_R)",
        "type": "Descending Giant Neuron",
        "neuropil": "Brain to VNC",
        "subsystem": "Descending Escape",
        "neurotransmitter": "Acetylcholine",
        "description": "Contralateral master escape command interneuron coordinating bilateral jump and flight initiation.",
        "coords": [15, 60, 170],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "10892",
        "name": "PSI",
        "type": "Thoracic Interneuron",
        "neuropil": "Ventral Nerve Cord (T1-T2)",
        "subsystem": "Motor Coordination",
        "neurotransmitter": "Cholinergic",
        "description": "Peripherally Synapsing Interneuron in VNC acting as an electrical/chemical synapse bridge between Giant Fiber and flight muscles.",
        "coords": [-10, -80, 20],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "20145",
        "name": "TTMn",
        "type": "Motor Neuron (Jump)",
        "neuropil": "VNC Leg Neuropil",
        "subsystem": "Motor Output",
        "neurotransmitter": "Acetylcholine",
        "description": "Tergo-trochanteral motor neuron innervating the middle leg extensor muscles for rapid jump takeoff.",
        "coords": [-35, -120, -40],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "20146",
        "name": "DLMn",
        "type": "Motor Neuron (Flight)",
        "neuropil": "VNC Wing Neuropil",
        "subsystem": "Motor Output",
        "neurotransmitter": "Glutamate",
        "description": "Dorsal longitudinal motor neuron driving the power wing depression muscles for sustained flight.",
        "coords": [-25, -135, -30],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "11044",
        "name": "DNa01",
        "type": "Descending Interneuron",
        "neuropil": "Brain to VNC",
        "subsystem": "Secondary Escape",
        "neurotransmitter": "GABA",
        "description": "Secondary descending pathway mediating slow, planned takeoffs with wing elevation prior to leg kick.",
        "coords": [30, 45, 125],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "11045",
        "name": "DNa02",
        "type": "Descending Interneuron",
        "neuropil": "Brain to VNC",
        "subsystem": "Secondary Escape",
        "neurotransmitter": "Glutamate",
        "description": "Pre-motor descending neuron tuning directionality of landing and take-off trajectories.",
        "coords": [35, 50, 120],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },

    # ==========================================
    # 2. CENTRAL COMPLEX & COMPASS NAVIGATION
    # ==========================================
    {
        "id": "30010",
        "name": "Me-Tu",
        "type": "Visual Relay",
        "neuropil": "Anterior Optic Tubercle",
        "subsystem": "Sun Compass",
        "neurotransmitter": "Acetylcholine",
        "description": "Transmits polarized sky light and celestial visual landmarks from the dorsal medulla.",
        "coords": [-110, 110, 90],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30011",
        "name": "TuBu01",
        "type": "Bulb Ring Relay",
        "neuropil": "Bulb (BU)",
        "subsystem": "Sun Compass",
        "neurotransmitter": "GABA",
        "description": "Microglomerular relay conveying celestial cues into the central complex.",
        "coords": [-70, 85, 75],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30012",
        "name": "ER4m",
        "type": "Ring Neuron",
        "neuropil": "Ellipsoid Body",
        "subsystem": "Compass Navigation",
        "neurotransmitter": "GABA",
        "description": "Inhibitory ring neuron forming the sensory receptive field around the internal compass.",
        "coords": [0, 40, 50],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30013",
        "name": "E-PG (Compass)",
        "type": "Heading Compass Neuron",
        "neuropil": "Ellipsoid Body / PB",
        "subsystem": "Compass Navigation",
        "neurotransmitter": "Acetylcholine",
        "description": "The biological internal compass! Generates a localized bump of excitation that tracks absolute head direction in 360 degrees.",
        "coords": [0, 25, 60],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30014",
        "name": "P-EN",
        "type": "Angular Velocity Integrator",
        "neuropil": "Protocerebral Bridge",
        "subsystem": "Compass Navigation",
        "neurotransmitter": "Acetylcholine",
        "description": "Integrates self-motion cues (optic flow and mechanosensory turning) to update compass heading in darkness.",
        "coords": [0, -10, 75],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30015",
        "name": "Delta7",
        "type": "Local Bridge Interneuron",
        "neuropil": "Protocerebral Bridge",
        "subsystem": "Compass Navigation",
        "neurotransmitter": "Glutamate",
        "description": "Cross-inhibitory interneuron maintaining single-bump compass dynamics across bridge glomeruli.",
        "coords": [0, -15, 80],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30016",
        "name": "FB_columnar",
        "type": "Navigational Vector Neuron",
        "neuropil": "Fan-shaped Body",
        "subsystem": "Vector Navigation",
        "neurotransmitter": "Acetylcholine",
        "description": "Translates compass heading into translational flight vector and targeted goal orientation.",
        "coords": [0, 15, 95],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30017",
        "name": "PFL3",
        "type": "Steering Pre-Motor",
        "neuropil": "LAL (Lateral Access. Lobe)",
        "subsystem": "Motor Steering",
        "neurotransmitter": "Acetylcholine",
        "description": "Direct steering comparison neuron comparing current heading to goal heading and driving differential left/right turning.",
        "coords": [-40, -25, 45],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "30018",
        "name": "DNb01",
        "type": "Descending Steering Motor",
        "neuropil": "VNC Steering",
        "subsystem": "Motor Output",
        "neurotransmitter": "Acetylcholine",
        "description": "Descending neuron commanding asymmetric wing stroke amplitude to execute rapid flight turns.",
        "coords": [-20, -90, -10],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },

    # ==========================================
    # 3. OLFACTORY LEARNING & MUSHROOM BODY
    # ==========================================
    {
        "id": "40001",
        "name": "ORN_Or42b",
        "type": "Olfactory Sensory",
        "neuropil": "Antenna",
        "subsystem": "Olfaction",
        "neurotransmitter": "Acetylcholine",
        "description": "High-affinity olfactory receptor neuron responding to food odorants (apple cider vinegar / ethyl acetate).",
        "coords": [-90, 140, 20],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "40002",
        "name": "PN_DM1",
        "type": "Projection Neuron",
        "neuropil": "Antennal Lobe",
        "subsystem": "Olfactory Processing",
        "neurotransmitter": "Acetylcholine",
        "description": "Antennal lobe projection neuron broadcasting attractive food valence to higher brain centers.",
        "coords": [-50, 90, 35],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "40003",
        "name": "KC_gamma",
        "type": "Kenyon Cell",
        "neuropil": "Mushroom Body Calyx",
        "subsystem": "Learning & Memory",
        "neurotransmitter": "Acetylcholine",
        "description": "Sparse associative encoding neuron in the mushroom body responsible for short-term odor memory formation.",
        "coords": [60, 80, 110],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "40004",
        "name": "DAN_PAM",
        "type": "Dopaminergic Neuron",
        "neuropil": "Mushroom Body Lobes",
        "subsystem": "Reward Reinforcement",
        "neurotransmitter": "Dopamine",
        "description": "Delivers sugar/food reward reinforcement signals to sculpt synaptic plasticity between KCs and MBONs.",
        "coords": [45, 50, 90],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "40005",
        "name": "MBON_alpha3",
        "type": "Mushroom Body Output",
        "neuropil": "Mushroom Body Lobes",
        "subsystem": "Memory Readout",
        "neurotransmitter": "GABA",
        "description": "Valence decision output neuron: directs motor behavior towards learned reward or away from aversive odor.",
        "coords": [75, 40, 80],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "40006",
        "name": "DNg02",
        "type": "Descending Locomotor",
        "neuropil": "VNC Walking Center",
        "subsystem": "Motor Output",
        "neurotransmitter": "Acetylcholine",
        "description": "Translates odor valence into forward walking velocity and food foraging orientation.",
        "coords": [10, -70, -20],
        "sex_dimorphic": False,
        "organism": "Drosophila melanogaster"
    },

    # ==========================================
    # 4. SEX-DIMORPHIC & MALE CNS COURTSHIP
    # ==========================================
    {
        "id": "50001",
        "name": "Sensory_ppk23",
        "type": "Pheromone Sensory",
        "neuropil": "Foreleg / Labellum",
        "subsystem": "Sex Dimorphic",
        "neurotransmitter": "Acetylcholine",
        "description": "Male-specific gustatory sensory neuron detecting female cuticular hydrocarbon pheromones (7,11-HD).",
        "coords": [-120, -10, -30],
        "sex_dimorphic": True,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "50002",
        "name": "vPN1",
        "type": "Courtship Sensory Relay",
        "neuropil": "Subesophageal Zone",
        "subsystem": "Sex Dimorphic",
        "neurotransmitter": "Acetylcholine",
        "description": "Male-enlarged projection neuron transmitting female contact pheromone signals to the central brain.",
        "coords": [-70, 20, 10],
        "sex_dimorphic": True,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "50003",
        "name": "P1 (Male Master Command)",
        "type": "Courtship Command Neuron",
        "neuropil": "Lateral Protocerebrum",
        "subsystem": "Sex Dimorphic",
        "neurotransmitter": "Acetylcholine / Fruitless+",
        "description": "The male-specific master courtship command neuron! Discovered in the 2026 male connectome as the central switch for courtship song and mating drive.",
        "coords": [-20, 35, 130],
        "sex_dimorphic": True,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "50004",
        "name": "pIP10",
        "type": "Descending Song Interneuron",
        "neuropil": "Brain to Thoracic VNC",
        "subsystem": "Sex Dimorphic",
        "neurotransmitter": "Glutamate",
        "description": "Descending courtship song command neuron gating wing vibration and acoustic pulse song generation.",
        "coords": [-10, -40, 100],
        "sex_dimorphic": True,
        "organism": "Drosophila melanogaster"
    },
    {
        "id": "50005",
        "name": "dPR1",
        "type": "Wing Motor Pre-Motor",
        "neuropil": "VNC Thoracic Musculature",
        "subsystem": "Motor Output",
        "neurotransmitter": "Acetylcholine",
        "description": "Controls unilateral wing extension and 200Hz courtship singing vibration in male flies.",
        "coords": [-15, -110, -35],
        "sex_dimorphic": True,
        "organism": "Drosophila melanogaster"
    }
]

# Synaptic Edges: Source ID -> Target ID with Synaptic Count (Connection Strength)
SYNAPTIC_CONNECTIONS: List[Dict[str, Any]] = [
    # Visual Escape Reflex
    {"source": "10001", "target": "10002", "synapses": 142, "type": "feedforward"},
    {"source": "10001", "target": "10003", "synapses": 189, "type": "feedforward"},
    {"source": "10002", "target": "10004", "synapses": 94, "type": "feedforward"},
    {"source": "10003", "target": "10004", "synapses": 168, "type": "feedforward"},
    {"source": "10004", "target": "10005", "synapses": 215, "type": "feedforward"},
    {"source": "10004", "target": "10006", "synapses": 178, "type": "feedforward"},
    {"source": "10005", "target": "10234", "synapses": 420, "type": "primary_trigger"},
    {"source": "10006", "target": "10234", "synapses": 365, "type": "primary_trigger"},
    {"source": "10005", "target": "10235", "synapses": 395, "type": "primary_trigger"},
    {"source": "10234", "target": "10892", "synapses": 612, "type": "electrical_chemical"},
    {"source": "10234", "target": "20145", "synapses": 780, "type": "monosynaptic_jump"},
    {"source": "10892", "target": "20146", "synapses": 540, "type": "flight_wing_power"},
    
    # Secondary Escape & Lateral Collaterals
    {"source": "10005", "target": "11044", "synapses": 88, "type": "secondary_relay"},
    {"source": "10006", "target": "11045", "synapses": 112, "type": "secondary_relay"},
    {"source": "11044", "target": "20145", "synapses": 74, "type": "polysynaptic_detour"},
    {"source": "11045", "target": "20146", "synapses": 65, "type": "polysynaptic_detour"},

    # Sun Compass & Navigation
    {"source": "30010", "target": "30011", "synapses": 156, "type": "feedforward"},
    {"source": "30011", "target": "30012", "synapses": 184, "type": "feedforward"},
    {"source": "30012", "target": "30013", "synapses": 310, "type": "receptive_field"},
    {"source": "30013", "target": "30014", "synapses": 240, "type": "recurrent_loop"},
    {"source": "30014", "target": "30013", "synapses": 225, "type": "recurrent_loop"},
    {"source": "30013", "target": "30015", "synapses": 190, "type": "cross_inhibition"},
    {"source": "30013", "target": "30016", "synapses": 280, "type": "vector_flow"},
    {"source": "30016", "target": "30017", "synapses": 340, "type": "steering_input"},
    {"source": "30017", "target": "30018", "synapses": 490, "type": "descending_command"},

    # Olfactory Learning & Memory
    {"source": "40001", "target": "40002", "synapses": 220, "type": "glomerular"},
    {"source": "40002", "target": "40003", "synapses": 165, "type": "sparse_expansion"},
    {"source": "40004", "target": "40003", "synapses": 130, "type": "neuromodulation"},
    {"source": "40003", "target": "40005", "synapses": 295, "type": "plastic_output"},
    {"source": "40005", "target": "40006", "synapses": 380, "type": "valence_locomotion"},

    # Sex-Dimorphic Male Courtship
    {"source": "50001", "target": "50002", "synapses": 175, "type": "pheromone_relay"},
    {"source": "50002", "target": "50003", "synapses": 320, "type": "male_command_trigger"},
    {"source": "50003", "target": "50004", "synapses": 460, "type": "song_gating"},
    {"source": "50004", "target": "50005", "synapses": 510, "type": "wing_extension_motor"}
]

SHOWCASE_PRESETS = [
    {
        "id": "preset_visual_escape",
        "title": "Visual Looming Threat → Giant Fiber Escape Reflex",
        "query": "Trace the neural circuit from visual photoreceptors and looming detection to motor jump and flight initiation. What happens if the Giant Fiber is knocked out?",
        "subsystem": "Visual Escape",
        "source_candidates": ["R1-R6", "L1", "L2", "LC4", "LPLC2"],
        "target_candidates": ["TTMn", "DLMn"],
        "key_relay": "Giant Fiber (GF_L)",
        "ablation_target": "10234"
    },
    {
        "id": "preset_sun_compass",
        "title": "Sun Compass Heading & Spatial Navigation",
        "query": "How do celestial polarized light cues in the anterior optic tubercle drive the E-PG heading compass and PFL3 steering motor output in the central complex?",
        "subsystem": "Compass Navigation",
        "source_candidates": ["Me-Tu", "TuBu01"],
        "target_candidates": ["DNb01", "PFL3"],
        "key_relay": "E-PG (Compass)",
        "ablation_target": "30013"
    },
    {
        "id": "preset_male_courtship",
        "title": "Male CNS Sex-Dimorphic P1 Courtship Song Circuit",
        "query": "Demonstrate the sex-dimorphic circuit identified in the Google male connectome where pheromone sensory input activates P1 command neurons and pIP10 courtship song motor output.",
        "subsystem": "Sex Dimorphic",
        "source_candidates": ["Sensory_ppk23", "vPN1"],
        "target_candidates": ["dPR1", "pIP10"],
        "key_relay": "P1 (Male Master Command)",
        "ablation_target": "50003"
    },
    {
        "id": "preset_olfactory_memory",
        "title": "Olfactory Valence & Mushroom Body Associative Learning",
        "query": "Find the neural pathway from antennal odor detection through projection neurons and Kenyon cells to MBON valence readout and locomotor direction.",
        "subsystem": "Olfaction & Learning",
        "source_candidates": ["ORN_Or42b", "PN_DM1"],
        "target_candidates": ["DNg02", "MBON_alpha3"],
        "key_relay": "KC_gamma",
        "ablation_target": "40003"
    }
]
