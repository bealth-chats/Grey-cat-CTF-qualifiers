from pwn import *
context.log_level = 'error'
libc = ELF('libc_2.35.so', checksec=False)

# Let's see if there's any `endbr64` gadget that aligns the stack or fixes the %rdx issue.
# We want something like `mov rdx, 0` or `xor edx, edx` that has `endbr64` and then calls/jumps to a register we control, or `execve`/`system`.
for g in libc.search(asm('xor edx, edx')):
    # check if it's near endbr64
    pass
print("done")
