# BabyRSA Writeup

## Introduction
This challenge asks us to decrypt a secret message (the "flag") that has been encrypted using a modified version of the popular RSA encryption algorithm.

In standard RSA, you generate two large random prime numbers, $p$ and $q$. You multiply them together to get a number called $N$ (so $N = p \times q$). $N$ is public and is used by others to encrypt messages to you. The security of standard RSA relies on the fact that if someone only knows $N$, it's incredibly difficult for them to figure out what $p$ and $q$ were. But if you *do* know $p$ and $q$, you can easily decrypt any messages sent to you!

In this "BabyRSA" challenge, the standard RSA setup has been tweaked in a dangerous way, allowing us to mathematically break it and find $p$ and $q$. Let's see how!

## The Vulnerability

Looking at the provided Python script `challenge.py`, we can see two major deviations from standard RSA:

1.  **Modified $N$**: Instead of $N = p \times q$, the challenge uses $N = (p^2) \times q$.
2.  **Information Leak**: The challenge provides us with `p_msb`, which stands for the "most significant bits" of $p$. Essentially, it tells us the first part of the prime number $p$, but leaves the last 320 bits hidden.

These two pieces of information are fatal to the security of this encryption!

Because we have a large portion of $p$ (`p_msb`), and because $p$ appears as $p^2$ inside $N$, we can use an advanced mathematical technique called **Coppersmith's Method**. This method allows us to find small missing pieces (roots) of a mathematical equation. In our case, the missing piece is the last 320 bits of $p$.

By constructing a polynomial equation around what we know about $p$ and $N$, Coppersmith's Method can efficiently guess the remaining missing bits of $p$.

## The Solution

We used **SageMath**, a powerful open-source mathematics software system, to solve this. SageMath has built-in functions for Coppersmith's method, specifically `small_roots()`.

Here are the steps our script takes:

1.  **Set up the equation**: We tell SageMath that $p = p\_msb + x$, where $x$ is the small missing piece we want to find. We know that $p$ is a factor of $N$, which means $p^2$ is also a factor of $N$. So, we look for solutions to $(p\_msb + x)^2 \equiv 0 \pmod N$.
2.  **Find the missing bits**: We use the `small_roots()` function in SageMath, telling it roughly how big $x$ should be (up to $2^{320}$).
3.  **Reconstruct $p$ and $q$**: Once SageMath finds the missing $x$, we add it back to `p_msb` to get the full prime number $p$. With $p$ in hand, finding $q$ is easy: $q = N / (p^2)$.
4.  **Decrypt the flag**: Now that we have $p$ and $q$, we have everything we need to break the RSA encryption. We use the standard RSA decryption mathematical formulas to unlock the ciphertext $c$ and reveal our flag.

### SageMath Script

```python
# The given values from the challenge
N = 5719300... # (Truncated for brevity)
e = 65537
c = 3453154...
p_msb = 1791474...

# Tell SageMath to look for numbers in the realm of N
P.<x> = PolynomialRing(Zmod(N))

# We know p = p_msb + x, and p^2 is a factor of N
f = (p_msb + x)^2

# Use Coppersmith's method to find x (up to 2^320)
roots = f.small_roots(X=2^320, beta=0.6)

if roots:
    print("Found root:", roots[0])

    # Reconstruct p
    p = p_msb + int(roots[0])

    # Calculate q
    q = N // (p^2)

    # Standard RSA decryption steps
    phi = p * (p - 1) * (q - 1)
    d = inverse_mod(e, phi)
    m = pow(c, d, N)

    # Convert the decrypted number back into text
    import binascii
    h = hex(int(m))[2:]
    if len(h) % 2 == 1:
        h = '0' + h
    print("flag:", binascii.unhexlify(h).decode())
else:
    print("No roots found")
```

Running this script successfully uncovers the missing piece of $p$, reconstructs the primes, and decrypts the secret message to reveal:

`grey{th1s_15_pr0b4bly_t00_34sy_n0w4d4y5_1n34v80n23}`