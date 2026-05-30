from pwn import *
libc = ELF('libc_2.35.so', checksec=False)

# Since we don't have a gadget, let's rethink:
# `name[0]` must be 0 for envp to be valid.
# So `%rdi` points to an empty string.
# But wait... does `%rdi` HAVE to point to `"/bin/sh"`?
# What if we create a file whose name is `""` (empty string)?
# We can't! Empty string is not a valid filename in Linux!
# `execve("", argv, envp)` always returns `ENOENT`.

# Wait... what if we find a gadget that does `mov rdx, 0` and then `call *%rax`? No.
# What about a gadget that calls `system` internally?
# Is there a function in libc that takes a pointer, does some parsing, and calls `system`?
# E.g. `wordexp`?
# `wordexp` parses a string and might call a shell!
# Does `wordexp` use `movaps`? Yes, probably.

# What about `do_system`? It's at 50900. It doesn't have `endbr64`.
# Can we jump to `system` at 50d70, but make sure `%rsp` is 16-byte aligned?
# We need `call system` to happen with `%rsp` 0 mod 16.
# If we overwrite `speak` with `system`, `talk` calls it.
# `talk()`:
# push rbp (8)
# sub rsp, 0x10 (16)
# call *rax (8)
# If we overwrite `speak` with `talk` itself!
# `talk` takes `Greycat*` in `%rdi`.
# `talk(name)` -> `name` is treated as `Greycat*`!
# So `name[0x28]` is the NEXT `speak` pointer!
# And what does `talk` do to the stack?
# It pushes `rbp`, `sub 0x10`, `call *rax`.
# This is a 32-byte shift! (8 + 16 + 8).
# 32 bytes is 0 mod 16!
# So calling `talk` AGAIN DOES NOT CHANGE THE MOD 16 ALIGNMENT!
# We said `%rsp` is 8 mod 16 when `speak` is called.
# If `speak` is `talk`, `%rsp` will be 8 mod 16 when the inner `speak` is called!
# Wait!
# 8 + 32 = 40. 40 mod 16 = 8.
# Yes, it is still 8 mod 16!
# So calling `talk` again does NOT help!

# What if we overwrite `speak` with `printmenu`?
# `printmenu` takes NO arguments. But it pushes `rbp`, etc.
# 1979: endbr64
# 197d: push rbp
# 197e: mov rsp, rbp
# 1981: lea rax, ...
# 1988: mov rdi, rax
# 198b: call cout
# ...
# 199b: pop rbp
# 199c: ret
# `printmenu` doesn't call our function pointer. So we can't chain.
