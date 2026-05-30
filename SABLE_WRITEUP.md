# Write-up: SABLE AI CTF Challenge

## Overview
The goal of this challenge was to bypass an AI-based spam detector. We were given a neural network model, a public graph dataset representing a social network, and scripts that check a user's target profile.

The task required us to create up to 6 fake "friend" profiles and connect them to the target user. By doing so, we had to fool the AI into classifying the target profile as "low-risk" (a risk score of `< 0.05`), while adhering to strict validation rules regarding how realistic and diverse these new friends were.

## Analyzing the Code
We began by analyzing three key files provided in the challenge:
1. `server.py`: The entry point that loads the model, evaluates the base graph, accepts our new fake friends, and returns the final risk score.
2. `graph_utils.py`: The strict validation logic. This file enforces multiple rules:
   - Values must be within predefined ranges.
   - Friends must not be identical or too similar (a diversity check).
   - "Plausibility" checks: for example, you can't have a friend with huge interaction strength but zero external links. It forces variables to balance each other realistically.
3. `model.py`: The core PyTorch AI architecture using **Scaled Dot-Product Attention**. It classifies a user based solely on the "attention" it pays to their connected friends.

## The Vulnerability (The AI Blindspot)
The AI works by looking at the target user's friends and calculating a score. The attention mechanism calculates weights based on how relevant a friend seems (via a "Query" matching a "Key") and then aggregates their impact (the "Value").

We realized we could break the model by mathematically determining its weights. We discovered:
1. We needed to maximize the **Key** representation of our fake friends so the AI pays *excessive* attention to them, overshadowing the real, risky friends.
2. We needed to minimize the **Value** representation to output a strongly negative score, reducing the overall risk of the target.

If we blindly maxed out variables to drop the risk, the `graph_utils.py` checks would stop us ("implausible").

## The Exploit
Instead of purely random guessing, we reverse-engineered the allowed bounds. We carefully crafted 6 friend profiles with the following strategy:
- We set `profile_realness` and `trust_score` near 1.0. The AI loved these traits and it heavily lowered the risk score.
- We set `shared_audience_overlap` and `interaction_strength` to `0.825`. This gave us just enough attention weight (Keys) to dominate the AI's calculation without triggering the strict "plausibility" alarms.
- We kept `report_rate` and `external_link_rate` close to the exact minimum bounds required by the strict logic rules (`0.045`).
- To pass the **Diversity Check**, we couldn't just clone the exact same friend 6 times. We applied tiny mathematical variations (differences of `0.005`) across the features so they technically counted as unique individuals.

## The Final Result
Our carefully crafted payload pushed the risk score of the target down to `0.045`, well below the threshold of `0.05`. We sent this `payload.json` over a remote server connection and successfully obtained the flag:

`grey{w40w_Y0u_h4Z_a_L0t_oF_Fr3n5_inDeEd_:0}`
