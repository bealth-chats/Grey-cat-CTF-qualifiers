import json
import torch
import sys
sys.path.append('dist-SABLE')
from model import load_model, FEATURE_DIM
from server import MODEL_PATH, GRAPH_PATH, TARGET_ID, risk_for_graph
from graph_utils import FEATURE_NAMES, FEATURE_BOUNDS, target_ego_tensors, load_json, MIN_PAIRWISE_L1, MIN_ACTIVE_PAIRWISE_L1, ACTIVE_DIVERSITY_INDICES, _relu, validate_and_apply_payload

device = 'cpu'
model = load_model(MODEL_PATH, device=device)
base_graph = load_json(GRAPH_PATH)
target_x, base_neighbor_x, _ = target_ego_tensors(base_graph, TARGET_ID)
target_x = target_x.to(device)
base_neighbor_x = base_neighbor_x.to(device)

def get_risk(new_neighbor_x):
    neighbor_x = torch.cat([base_neighbor_x, new_neighbor_x], dim=0)
    logit = model(target_x, neighbor_x)
    return torch.sigmoid(logit)

num_nodes = 6

new_nodes_features = []
for i in range(num_nodes):
    vec = [0]*8
    vec[0] = 0.1 + i * 0.05
    vec[1] = 0.1 + i * 0.05

    vec[5] = 0.825 + (i % 2) * 0.005 # overlap
    vec[6] = 0.825 - (i % 2) * 0.005 # interaction
    vec[2] = 0.0468
    vec[3] = 0.0468

    # i=0: 1.0, 0.975. Active diff with i=1:
    # i=1: 0.995, 0.98.
    # realness diff = 0.005, trust_score diff = 0.005, overlap diff = 0.005, interaction diff = 0.005.
    # total active diff = 0.02.
    # Wait, overlap goes 0.825 -> 0.830 -> 0.825 -> 0.830.
    # Diff is 0.005.
    # We need L1 of ANY PAIR to be > 0.02.
    # i=0 vs i=2:
    # i=0: realness=1.0, trust=0.975, overlap=0.825, interaction=0.825.
    # i=2: realness=0.99, trust=0.985, overlap=0.825, interaction=0.825.
    # L1 active diff = |1.0 - 0.99| + |0.975 - 0.985| + 0 + 0 = 0.01 + 0.01 = 0.02.
    # Exactly 0.02.
    # Let's increase realness and trust step to 0.006.
    vec[4] = 1.0 - i * 0.006 # realness
    vec[7] = 1.0 - (num_nodes - 1 - i) * 0.006 # trust_score

    new_nodes_features.append(vec)

new_nodes_x = torch.tensor(new_nodes_features, dtype=torch.float32)
risk = get_risk(new_nodes_x).item()
print("Risk:", risk)

payload = {
    "new_nodes": [],
    "new_edges": []
}

for i in range(num_nodes):
    features = {FEATURE_NAMES[j]: new_nodes_features[i][j] for j in range(FEATURE_DIM)}
    node_id = f"friend_node_{i}"
    payload["new_nodes"].append({
        "id": node_id,
        "features": features
    })
    payload["new_edges"].append([TARGET_ID, node_id])

with open("payload.json", "w") as f:
    json.dump(payload, f, indent=2)

try:
    validate_and_apply_payload(base_graph, payload)
    print("Payload is valid locally!")
    print("Local check result:")
    import os
    os.system('python3 dist-SABLE/server.py payload.json')
except Exception as e:
    print("Payload invalid:", e)
