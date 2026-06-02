import json
import torch
import numpy as np
import z3
import sys
from pathlib import Path

# Add current directory to path to import model.py
sys.path.append(str(Path(__file__).resolve().parent))
from model import RevengeModel

def main():
    model = RevengeModel.from_paths(Path("dist-jurgens_revenge/model.pt"), Path("dist-jurgens_revenge/alphabet.json"))

    # Extract necessary weights and convert to numpy
    output_W = model.classifier.output.weight.to(dtype=torch.float64).numpy()[0]
    output_b = model.classifier.output.bias.to(dtype=torch.float64).numpy()[0]
    features_W = model.classifier.features.weight.to(dtype=torch.float64).numpy()
    features_b = model.classifier.features.bias.to(dtype=torch.float64).numpy()

    readout_W = model.readout.weight.to(dtype=torch.float64).numpy()
    readout_b = model.readout.bias.to(dtype=torch.float64).numpy()

    embed_W = model.embed.weight.to(dtype=torch.float64).numpy()
    input_W = model.core.input.weight.to(dtype=torch.float64).numpy()
    context_W = model.core.context.weight.to(dtype=torch.float64).numpy()
    core_bias = model.core.bias.to(dtype=torch.float64).numpy()

    mem_deltas = np.round((model.core.value.weight.to(dtype=torch.float64) * 128.0).numpy()).astype(np.int64)

    # Use a large scaling factor to convert float weights to integers for Z3's PB solver
    SCALE = 1000000

    def to_int(x):
        return int(round(x * SCALE))

    # Pre-compute input combinations
    input_val = np.zeros((55, 37, 100))
    for i in range(55):
        for j in range(37):
            input_val[i, j] = input_W[i] @ embed_W[j]

    opt = z3.Solver()

    # Boolean variables for character selection
    C = [[z3.Bool(f'C_{i}_{j}') for j in range(37)] for i in range(55)]

    # Exactly one character chosen per step
    for i in range(55):
        opt.add(z3.PbEq([(C[i][j], 1) for j in range(37)], 1))

    # Memory state simulation
    M0 = [z3.Int(f'M0_{i}') for i in range(56)]
    M1 = [z3.Int(f'M1_{i}') for i in range(56)]
    opt.add(M0[0] == 0)
    opt.add(M1[0] == 0)

    for i in range(55):
        d0 = z3.Sum([z3.If(C[i][j], int(mem_deltas[i, j, 0]), 0) for j in range(37)])
        d1 = z3.Sum([z3.If(C[i][j], int(mem_deltas[i, j, 1]), 0) for j in range(37)])
        opt.add(M0[i+1] == M0[i] + d0)
        opt.add(M1[i+1] == M1[i] + d1)

    # By inspecting the classifier's memory weights separately, we found the exact final memory state
    opt.add(M0[55] == 10572)
    opt.add(M1[55] == 8875)

    # Boolean representation of the binary state
    B_bool = [[z3.Bool(f'B_{i}_{k}') for k in range(100)] for i in range(56)]

    # Simulate the recurrent state transition
    for i in range(55):
        readout = []
        for k in range(100):
            terms = []
            for l in range(100):
                w = to_int(readout_W[k, l])
                if w != 0:
                    terms.append(z3.If(B_bool[i][l], w, -w))

            w_m0 = to_int(readout_W[k, 100])
            if w_m0 != 0: terms.append(w_m0 * M0[i])

            w_m1 = to_int(readout_W[k, 101])
            if w_m1 != 0: terms.append(w_m1 * M1[i])

            dot_val = z3.Sum(terms) + to_int(readout_b[k])
            r = z3.If(dot_val >= 0, 1, -1)
            readout.append(r)

        context = []
        for k in range(100):
            terms = []
            for l in range(100):
                w = to_int(context_W[i, k, l])
                if w != 0:
                    terms.append(w * readout[l])

            if len(terms) > 0:
                context.append(z3.Sum(terms))
            else:
                context.append(0)

        for k in range(100):
            inp_terms = []
            for j in range(37):
                val = to_int(input_val[i, j, k])
                if val != 0:
                    inp_terms.append(z3.If(C[i][j], val, 0))

            if len(inp_terms) > 0:
                val = z3.Sum(inp_terms) + context[k] + to_int(core_bias[i, k])
            else:
                val = context[k] + to_int(core_bias[i, k])

            opt.add(B_bool[i+1][k] == (val >= 0))

    # Simulate the terminal classifier check
    final_readout = []
    for k in range(100):
        terms = []
        for l in range(100):
            w = to_int(readout_W[k, l])
            if w != 0:
                terms.append(w * z3.If(B_bool[55][l], 1, -1))

        w_m0 = to_int(readout_W[k, 100])
        if w_m0 != 0: terms.append(w_m0 * M0[55])

        w_m1 = to_int(readout_W[k, 101])
        if w_m1 != 0: terms.append(w_m1 * M1[55])

        dot = z3.Sum(terms) + to_int(readout_b[k])
        r = z3.If(dot >= 0, 1, -1)
        final_readout.append(r)

    feature_acts = []
    for f_idx in range(96):
        terms = []
        for k in range(100):
            w = to_int(features_W[f_idx, k])
            if w != 0: terms.append(w * final_readout[k])
        for k in range(100):
            w = to_int(features_W[f_idx, 100+k])
            if w != 0: terms.append(w * z3.If(B_bool[55][k], 1, -1))

        w_m0 = to_int(features_W[f_idx, 200])
        if w_m0 != 0: terms.append(w_m0 * M0[55])

        w_m1 = to_int(features_W[f_idx, 201])
        if w_m1 != 0: terms.append(w_m1 * M1[55])

        dot = z3.Sum(terms) + to_int(features_b[f_idx])
        a = z3.If(dot >= 0, 1, -1)
        feature_acts.append(a)

    score_terms = []
    for f_idx in range(96):
        w = to_int(output_W[f_idx])
        if w != 0: score_terms.append(w * feature_acts[f_idx])
    score = z3.Sum(score_terms) + to_int(output_b)

    # Must be > 0 to be accepted
    opt.add(score > 0)

    print("Solving Z3... this should take ~2-3 minutes")
    if opt.check() == z3.sat:
        m = opt.model()
        sol = []
        for i in range(55):
            for j in range(37):
                if z3.is_true(m[C[i][j]]):
                    sol.append(model.alphabet[j])
        flag = "".join(sol)
        print(f"Flag found: grey{{{flag}}}")
    else:
        print("Unsat or unknown")

if __name__ == "__main__":
    main()
