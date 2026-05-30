# If we overwrite `speak` with `vwarnx` (120e50):
# 120e50: endbr64
# 120e54: xor edx, edx
# 120e56: jmp 120d20
# 120d20: endbr64
# 120d24: push r13
# 120d26: mov r13d, edx  <-- r13d = 0
# 120d29: push r12
# 120d2b: mov r12, rsi
# 120d2e: lea rsi, ...
# This eventually calls `vfprintf` which crashes because of `movaps`!
# So it doesn't give us `execve` and it still crashes!

# Wait! What if we use a gadget that aligns the stack, AND returns without crashing?
# Are there any `endbr64; ...; ret` gadgets that adjust `%rsp`?
# E.g., `endbr64; push ...; ret`?
# In rop22 I searched for `endbr64; ret`, but it didn't help.
