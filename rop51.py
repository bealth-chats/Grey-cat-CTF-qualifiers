from pwn import *
context.arch = 'amd64'
libc = ELF('libc_2.35.so', checksec=False)

for g in libc.search(asm('xchg rsp, rdi; ret')):
    print(hex(g))
for g in libc.search(asm('mov rsp, rdi; ret')):
    print(hex(g))
