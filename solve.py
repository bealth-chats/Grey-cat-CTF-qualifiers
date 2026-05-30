import pickle
import numpy as np
import re

def main():
    # Load parameters
    params = pickle.load(open('dist-duality_in_all_things/svc_dual_params.pkl', 'rb'))
    support_vectors_ = params.support_vectors_
    dual_coef_ = params.dual_coef_[0]
    intercept_ = params.intercept_[0]

    # Calculate weights and margins
    w = np.dot(dual_coef_, support_vectors_)
    y = np.sign(dual_coef_)
    margins = y * (np.dot(support_vectors_, w) + intercept_)

    # Calculate slack variables: xi_i = max(0, 1 - y_i(w^T x_i + b))
    slacks = np.maximum(0, 1 - margins)

    # Filter out slacks that are essentially 0
    valid_slacks = [s for s in slacks if s > 0.01]

    # Convert slacks to binary string based on their value
    # ~0.44-0.45 maps to '0'
    # ~0.74-0.75 maps to '1'
    binary_str = ''
    for s in valid_slacks:
        if abs(s - 0.44) < 0.02 or abs(s - 0.45) < 0.02:
            binary_str += '0'
        elif abs(s - 0.74) < 0.02 or abs(s - 0.75) < 0.02:
            binary_str += '1'

    # Convert binary string to ASCII characters
    chars = [chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)]
    res = ''.join(chars)

    # Extract flag
    match = re.search(r'grey\{.*?\}', res)
    if match:
        print(f"Found flag: {match.group(0)}")
    else:
        print("Flag not found")

if __name__ == '__main__':
    main()
