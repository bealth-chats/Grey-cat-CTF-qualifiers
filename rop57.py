# If SHSTK is enabled, EVERY `ret` must be paired with a `call`!
# So even if we find an `endbr64; push x; ret` gadget, `ret` will CRASH because it pops from the shadow stack and compares it with the regular stack!
# If we didn't use `call` to get to the gadget (we used `call *%rax` in `talk()`), the shadow stack has `talk() + 0x25` as the return address!
# If we do `push x; ret`, the regular stack pops `x`, but the shadow stack pops `talk() + 0x25`!
# They DON'T match! So it CRASHES!
# Therefore, ANY gadget ending in `ret` is USELESS if we modify the return address!
# But wait! We did NOT modify the return address!
# `call *%rax` pushed `talk() + 0x25`.
# If we jump to `endbr64; ret`, the regular stack pops `talk() + 0x25`, and the shadow stack pops `talk() + 0x25`. They MATCH! So it returns to `talk()`!
# BUT it doesn't help us execute `system`!

# If we want to execute `system`, we MUST jump to it directly!
# We jump to `system`, and it crashes because `%rsp` is 8 mod 16.
# If there is ANY way to jump to `system` with `%rsp` 0 mod 16, we win.
# Or if we can call `execve` with `%rdx = NULL` or valid pointer, we win.
# Or if there is a Magic Gadget (one_gadget) that works.
# Let's check `one_gadget` constraints again!
# 0xebc81: r10 == NULL, [rbp-0x70] == NULL
# 0xebc85: r10 == NULL, rdx == NULL
# 0xebc88: rsi == NULL, rdx == NULL
# 0xebce2: r13 == "/bin/sh", [r12] == NULL
# 0xebd38: r12 == "/bin/sh", [[rbp-0x70]] == NULL
# 0xebd3f: rax == NULL
# 0xebd43: rax == NULL

# We KNOW that `rax` is NOT NULL (it is the gadget address).
# We KNOW that `rdx` is `name`.
# What about `r10`, `rsi`, `r12`, `r13`, `rbp`?
