# Write-up for Jurgen's Revenge

This challenge provides a PyTorch model (`model.pt`) and an alphabet JSON mapping. Based on the name "Jurgen's Revenge" and the description (marginalized from deep learning canon), this is a reference to Jurgen Schmidhuber, the inventor of LSTMs. The model functions as a flag checker via a custom Recurrent Neural Network (RNN).

The flag has exactly 55 characters wrapped inside `grey{...}`. The checking mechanism returns `accepted` if a calculated final score is greater than 0.

## Inspecting the Model

1. **Architecture Overview:**
   The model is built with several custom layers simulating a recurrent architecture:
   - **Embedding:** Maps a 37-character alphabet to a 49-dimensional vector.
   - **Recurrent Core:** Maintains a `packed` state of 102 dimensions:
     - Indices `[0:100]` represent the binary boolean state space.
     - Indices `[100:102]` function as a 2D memory accumulator.
   - **Activation function (`act`):** Everything revolves around a sign activation step (`x >= 0` evaluates to 1, else -1). This is incredibly important because it limits the main binary state space strictly to `1` or `-1` values.

2. **Memory Accumulator (`model.core.value.weight`):**
   The memory explicitly updates strictly by simple addition of scaled Float16 vectors:
   ```python
   memory_next = memory_prev + self.core.value(step, char_index) * 128.0
   ```
   If we inspect this matrix, the values happen to be exact integers when scaled. There's no backpropagation or complex matrix multiplication—the memory state merely acts as a 2D integer constraint on the final output (similar to a multi-dimensional subset-sum/knapsack problem).

3. **Binary State (`model.core.candidate`):**
   The 100-dimensional binary state updates sequentially:
   ```python
   binary_next = sign(input_W @ embed + context_W @ sign(readout_W @ packed + readout_b) + bias)
   ```

4. **Classifier Head:**
   After consuming all 55 characters, the model runs a multi-layer linear classifier. If we inspect the final output weights:
   - There are 9 features with heavy positive weights (`~1.04`).
   - The bias is extremely negative (`-9.28`).
   - This mathematically proves that *all* 9 heavy features must be positively activated (`+1`) to achieve a `score > 0`.

## Formulating the constraints

Since there's no continuous nonlinearity like `tanh` or `sigmoid`, and the activation is purely boolean (`1` or `-1`), the model does not require gradient descent to solve. Instead, we can translate its exact weights and biases directly into constraints for a SAT/SMT solver like `Z3`.

### 1. Memory constraints
By inspecting the 9 heavy features, 4 of them are purely reliant on the memory accumulator. Setting these features to `>0` isolates exactly the target accumulated value for `memory[0]` and `memory[1]`:
- `memory[0] = 10572`
- `memory[1] = 8875`

### 2. Binary constraint propagation
To scale to Z3 effectively without performance drops:
- Since all components are based on inequalities `W @ x + b >= 0`, we multiply every float value by `1,000,000` (`1e6`) and round to the nearest integer.
- This lets Z3 operate natively on Pseudo-Boolean combinations of sums, which it optimizes extremely well.
- The `readout` weights natively have 99% sparsity, so filtering out zero weights dramatically reduces the Z3 equation sizes.

## Z3 Script

We define variables:
- `C[step][char]` (boolean matrix of choices)
- `M0[step]`, `M1[step]` (running memory totals)
- `B[step][k]` (boolean representations of the state, `1` if `True`, `-1` if `False`)

After simulating the exact model transitions within Z3, setting up the equations, and executing the PB solver:

```
Solving Z3 with ALL non-zero weights...
Flag: h1y4_there_n3el_n4nda_d1dnt_s3e_y0u_0ver_fr0m_ov3r_h3re
```

## Wrapping up

Putting the solved sequence back into the flag format gives the accepted string.
**Flag:** `grey{h1y4_there_n3el_n4nda_d1dnt_s3e_y0u_0ver_fr0m_ov3r_h3re}`
