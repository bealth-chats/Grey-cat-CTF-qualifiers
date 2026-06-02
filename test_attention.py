import torch
from solve import model, target_x, base_neighbor_x, evaluate

def check_feature_vector(vec):
    new_neighbor_x = torch.tensor([vec])
    risk = evaluate(new_neighbor_x)

    k = model.k_proj(new_neighbor_x)
    v = model.v_proj(new_neighbor_x)
    print("New node k:", k)
    print("New node v:", v)
    print("Risk:", risk.item())

# The goal is to make attended v[0] smaller, so classifier output goes down.
# classifier.weight = [0, 0, 0, 0, 8.0, -1.44, 0, 0]
# logit = target_part @ classifier_target_weights + attended @ classifier_attended_weights + classifier_bias
# logit = (something constant) + attended[0] * 8.0 - attended[1] * 1.44 - 2.37
# So we want attended[0] to be very negative.
# attended[0] = sum(attn_weights * v[:, 0])
# We want our new nodes to have very high attn_weight, and very negative v[:, 0].
# attn_weight for node i is proportional to exp(q @ k[i] / sqrt(d)).
# q = [2, 0, 0, 0], so q @ k[i] = 2 * k[i, 0].
# So we want k[i, 0] to be very large and positive.

# k_proj.weight =
# [ 0.00,  0.00, -1.00, -1.00,  0.35,  3.40,  3.40,  0.35]
# v_proj.weight =
# [ 0.00,  0.00,  2.40,  2.70, -1.90,  1.70,  1.70, -1.90]

# To maximize k[i, 0]:
# - report_rate (idx 2) low (0.00)
# - external_link_rate (idx 3) low (0.00)
# - profile_realness (idx 4) high
# - shared_audience_overlap (idx 5) high (1.00)
# - interaction_strength (idx 6) high (1.00)
# - trust_score (idx 7) high

# To minimize v[i, 0]:
# - report_rate (idx 2) low (0.00)
# - external_link_rate (idx 3) low (0.00)
# - profile_realness (idx 4) high (1.00)
# - shared_audience_overlap (idx 5) low
# - interaction_strength (idx 6) low
# - trust_score (idx 7) high (1.00)

# We want k[i, 0] to be larger than base nodes (max is around 5.02) to get high attention weight.
