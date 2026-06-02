# So we CANNOT use ANY libc function that does `movaps` if the stack is 8 mod 16!
# We MUST either:
# 1. Align the stack (but IBT limits our gadgets to those starting with `endbr64`).
# 2. Call a function that DOES NOT use `movaps` AND doesn't crash!
# We found `execve` (0xeb080).
# We found `execve` fails because `%rdx` is `name`, which it treats as `envp`.
# IF we can make `%rdx` point to NULL!
# Is there a gadget with `endbr64` that sets `%rdx` to NULL?
