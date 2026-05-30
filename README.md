# Filter Flag

The server uses PCBC mode. The decryption for block `i` is `state_i = state_{i-1} \oplus AES.decrypt(c_i) \oplus c_i`.
This means `state_n = IV \oplus \bigoplus_{j=1}^n (AES.decrypt(c_j) \oplus c_j)`.

Because the XOR operation is commutative, if we swap `c_1` and `c_2`, the state after decrypting the first two blocks remains the same:
`state'_2 = state_2`.
This means that for the third block onwards, decryption proceeds exactly as normal.
Since the server prints the decrypted plaintext if the whole block is printable, and only returns `????????????????` otherwise, swapping `c_1` and `c_2` will result in garbled blocks for the first two blocks, but the remaining blocks will be decrypted perfectly!

Furthermore, to get the first blocks perfectly, we can just flip a bit in the last ciphertext block. This will garble the last plaintext block, but the previous blocks will be decrypted perfectly.

By combining these two modified ciphertexts, we can recover the entire flag.

Flag: `grey{7c0c6a199cda0a96b55e74c5e1394284655e623c68f72ba59e4eb9fdb4_W4h_uR_Q_gUd_4h}`
