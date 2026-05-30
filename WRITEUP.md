# Duality in All Things

## Challenge Description
Where there is Yin, there is Yang.
Where there is a primal problem, there is a dual problem.
Where there is regularization, there are oversteppers.
Where there are oversteppers, there is slack.
I wonder: Where there is a challenge, is there a flag?

## Solution

The challenge gives us a `.zip` archive containing `verify.py`, `requirements.txt` and `svc_dual_params.pkl`.
Loading the `svc_dual_params.pkl` file using the `pickle` module reveals it is a scikit-learn Support Vector Classifier (SVC) parameter namespace object.
It has the attributes `support_vectors_`, `dual_coef_`, `intercept_`, and `C`.

The description hints at SVM (Support Vector Machine) properties:
> Where there is a primal problem, there is a dual problem.

This references the primal and dual optimization problems for SVMs.

> Where there is regularization, there are oversteppers.
> Where there are oversteppers, there is slack.

This points to the concept of slack variables ($\xi_i$) in soft-margin SVMs. Slack variables allow some data points to be misclassified or fall inside the margin. They represent how much a support vector "oversteps" its margin boundary.

For a data point $x_i$ with label $y_i$, the slack variable is defined as:
$\xi_i = \max(0, 1 - y_i(w^T x_i + b))$

Where:
- $w$ is the weight vector, which can be computed from the dual parameters: $w = \sum_i \alpha_i y_i x_i = \text{dual\_coef} \cdot \text{support\_vectors}$
- $b$ is the bias or intercept: `intercept_`
- $x_i$ are the support vectors
- $y_i$ are the labels, which can be derived from the sign of the `dual_coef_`

Let's compute the slack variables:
```python
import pickle
import numpy as np
import re

# Load parameters
params = pickle.load(open('dist-duality_in_all_things/svc_dual_params.pkl', 'rb'))
support_vectors_ = params.support_vectors_
dual_coef_ = params.dual_coef_[0]
intercept_ = params.intercept_[0]
C = params.C

# Calculate weights and margins
w = np.dot(dual_coef_, support_vectors_)
y = np.sign(dual_coef_)
margins = y * (np.dot(support_vectors_, w) + intercept_)

# Calculate slack variables: xi_i = max(0, 1 - y_i(w^T x_i + b))
slacks = np.maximum(0, 1 - margins)
```

By printing the slack variables, we can see two values near 0 and many other values clustered around 0.44-0.45 and 0.74-0.75.

```python
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
```

Running this gives us the flag!

**Flag:** `grey{du4l_0pt1m1z4t10n_l3ft_th3_supp0rt_v3ct0rs_b3h1nd}`
