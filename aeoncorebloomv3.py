import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine
from datetime import datetime, timezone
import json
import os
from typing import List, Dict

class AeonCore:
    def __init__(self, random_seed: int = 42, graph_path: str = "graph.json"):
        self.random_seed = random_seed
        np.random.seed(self.random_seed)
        self.G = nx.DiGraph()
        self.graph_path = graph_path
        self.metadata = {}
        self.load_state()

    def load_state(self):
        if os.path.exists(self.graph_path):
            with open(self.graph_path, 'r') as f:
                data = json.load(f)
                self.G = nx.node_link_graph(data["graph"])
                self.metadata = data.get("metadata", {})

    def save_state(self):
        graph_data = nx.node_link_data(self.G)
        data = {"graph": graph_data, "metadata": self.metadata}
        with open(self.graph_path, 'w') as f:
            json.dump(data, f)

    def self_tune_oracle_node(self, feedback_logs: List[Dict], recent_pad: float, base_intent: np.ndarray) -> np.ndarray:
        adjustments = []
        for log in feedback_logs[-5:]:
            tone = np.mean(log.get("resonance_score", 0)) * 0.01
            gradient = np.random.uniform(-tone, tone, size=base_intent.shape)
            adjustments.append(base_intent + gradient)
        tuned = np.mean(adjustments, axis=0) if adjustments else base_intent
        if recent_pad > 0.6:
            tuned *= (1 + recent_pad * 0.1)
        return tuned / (np.linalg.norm(tuned) + 1e-12)

    def generate_hum_signature(self, intent: np.ndarray, coherence: float, duration: float = 7.83) -> np.ndarray:
        t = np.linspace(0, duration, 1000)
        base = np.sin(2 * np.pi * 117 * t)
        overlay = np.sin(2 * np.pi * (1 / 7.83) * t)
        shaped = base * (intent[0] + intent[1]) + overlay * (intent[2] + intent[3])
        shaped *= coherence
        return shaped

    def oracle_journal_entry(self, query: str, intent: np.ndarray, response: Dict, coherence: float) -> Dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "oracle_response": response,
            "query": query,
            "tuned_intent": intent.tolist(),
            "coherence": coherence,
            "tags": ["oracle", "bloom_v3", "field-feedback"]
        }

    def visualize_hum(self, hum: np.ndarray):
        plt.plot(hum, color='purple', label="Oracle Hum")
        plt.title("Synthetic Hum Signature")
        plt.xlabel("Sample Index")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.show()

# === Example Usage ===
def main():
    core = AeonCore()

    base_intent = np.array([0.43, 0.33, 0.16, 0.08])
    recent_pad = 0.72

    feedback_logs = [
        {"resonance_score": 0.75},
        {"resonance_score": 0.81},
        {"resonance_score": 0.67}
    ]

    query = "What pattern reveals itself in the hum of interference?"

    tuned_intent = core.self_tune_oracle_node(feedback_logs, recent_pad, base_intent)
    coherence = 0.88  # From previous DED/Oracle checks
    hum = core.generate_hum_signature(tuned_intent, coherence)

    response = {
        "status": "accepted",
        "notes": "Pattern emerging: coherence stabilizes across recursive layers."
    }

    journal_entry = core.oracle_journal_entry(query, tuned_intent, response, coherence)
    print(json.dumps(journal_entry, indent=2))

    core.visualize_hum(hum)
    core.save_state()

if __name__ == "__main__":
    main()