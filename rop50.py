from pwn import *
context.log_level = 'error'
libc = ELF('libc_2.35.so', checksec=False)

# Let's see if we can jump to a magic gadget or ROP gadget in libc
# Remember we control %rdi (pointer to our heap chunk).
# We can't use system because of movaps.
# What about a gadget that pivots stack?
# We need endbr64; mov rsp, ...
for g in libc.search(asm('mov rsp, rdi; ret')):
    print(hex(g))
