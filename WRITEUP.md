# AE-no-S Challenge Writeup

## The Challenge

In this cryptography challenge, we are presented with a modified version of the famous encryption algorithm, Advanced Encryption Standard (AES). The description gives us a hint: "So you know how the S in AES does not stand for SubBytes, but rather Standard? That clearly means SubBytes is NOT NECESSARY!!!! :D... right?"

AES uses a specific step called "SubBytes" (or S-box substitution). This is the *only* part of AES that is non-linear—meaning it introduces complex, unpredictable mathematical "mixing" that makes the encryption impossible to reverse with simple algebra.

The challenge removes this SubBytes step.

## The Flaw

Without the non-linear SubBytes step, everything else in AES (ShiftRows, MixColumns, AddRoundKey) is just basic linear algebra.

Imagine normal AES as a complex recipe where you bake a cake (non-linear). Once it's baked, you can't easily turn it back into eggs and flour.
But without the SubBytes "baking" step, AES just becomes a process of mixing ingredients in a specific, predictable way (like tossing a salad). If you know exactly how the ingredients were tossed, you can un-toss them.

In mathematical terms, the encryption behaves like a simple equation:
`Ciphertext = (Matrix A * Plaintext) + Constant B`

The challenge gives us a helpful file called `output.txt` which contains two things:
1. The ciphertext when the plaintext is all zeroes (this is our `Constant B`).
2. The ciphertexts for single-bit plaintexts (like a standard basis).

By subtracting `Constant B` from each of these standard basis ciphertexts, we can figure out exactly what `Matrix A` is.

## The Solution

Once we have `Matrix A` and `Constant B`, we can easily reverse the encryption.

If `C = (A * P) + B`, then reversing it is just:
`P = Inverse of A * (C - B)`

We wrote a solver script (`solve.py`) that does exactly this:
1. It reads the `Constant B` (the encryption of zero).
2. It constructs `Matrix A` using the 128 basis pairs provided in the output file.
3. It uses a method called "Gaussian Elimination" (a standard mathematical way to solve linear equations) to invert `Matrix A`.
4. It applies this inverse matrix to the encrypted flag (`flag_ct` in the output file) to recover the original plaintext.

## The Result

Running the solver script quickly performs the matrix inversion and spits out the original flag:

`grey{iT5_4LL_l1N3R_aLGyBeR?_a1WaY5_HaZ_B1n...}`
