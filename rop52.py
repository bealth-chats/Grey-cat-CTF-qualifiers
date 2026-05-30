# If SHSTK is enabled, we CANNOT PIVOT THE STACK!
# Because if we pivot `%rsp` to the heap, and then call `ret`, the SHADOW STACK pointer (`ssp`) is NOT PIVOTED!
# `ret` will try to pop the return address from the normal stack AND from the shadow stack.
# It will compare them. If they mismatch, it crashes.
# Since we didn't pivot the shadow stack, they WILL mismatch!
# So stack pivoting is completely dead unless we can forge the shadow stack (which we can't because it's read-only and randomized).

# This means we MUST use the existing stack!
# And we MUST not use `ret` gadgets!
# The ONLY way to get code execution is to call a function pointer that does what we want!
# Like `system("/bin/sh")`
# Or `execve("/bin/sh", NULL, NULL)`
# But we already established:
# 1. `system` crashes due to `movaps` because stack is 8 mod 16.
# 2. `execve` crashes because `%rdx` is `name` (a pointer to our string), so `execve` tries to read `name[0]` as an environment variable pointer!
# Since `name[0]` contains `"/bin/sh\x00"`, it treats `0x0068732f6e69622f` as a pointer and segfaults!
# If we set `name[0]` to 0 (NULL), `%rdx` points to 0, which is valid envp!
# BUT then `name` (which is `%rdi`) is `""`! So `execve` executes `""`, which returns `-ENOENT`!

# So we just need a way to make `%rdi` point to `"/bin/sh"` while `%rdx` points to a NULL array!
# We found some gadgets that shift `%rdi`!
# For example:
#   162a70: endbr64
#   162a74: mov rdi, [rdi+0x10]
#   162a78: mov rcx, rsi
#   162a7b: xor eax, eax
#   162a7d: mov rsi, rdx
#   162a80: movl $0x2, 0xc8(%rdi)
#   162a87: add rdi, 0xc8
#   162a91: jmp *rcx
# But this jumps to `*rcx` which is `%rsi`! `%rsi` is 0! So it jumps to 0 and crashes!

# Are there any OTHER gadgets that shift `%rdi` and then jump to something we control?
