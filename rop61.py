# If `puts` printed NOTHING (only the menu returned), it means `puts` crashed too!
# In libc 2.35, `puts` calls `strlen` internally which might use AVX instructions (`vmovdqa`, etc.) that require 16-byte or 32-byte alignment!
# So almost ANY libc function that handles strings (printf, puts, system) crashes when called with `%rsp` 8 mod 16 in GLIBC 2.35 due to AVX optimizations!

# So we MUST fix `%rsp` or we MUST use a function that DOES NOT use AVX/movaps.
# We found `execve` does not use `movaps` (it's a system call wrapper!).
# System call wrappers in libc are usually very simple:
#   mov eax, syscall_number
#   syscall
#   ret
# Let's check `execve` in libc 2.35!
