from pwn import *
import time
import subprocess

p = subprocess.Popen(['python3', 'solve_gdb.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
time.sleep(1)
pid = open('pid.txt').read().strip()
print("PID:", pid)

# GDB script to check registers right before call *rax
gdb_cmds = f"""
file ./dist-babyheap/babyheap
attach {pid}
b *0x00000000000019c1
continue
info reg
quit
"""
with open('gdb.cmd', 'w') as f:
    f.write(gdb_cmds)
