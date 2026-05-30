# YES! `execve` DOES NOT USE STACK!
# It just does `syscall` directly!
# So `execve` DOES NOT CRASH on 8 mod 16 alignment!
# The ONLY reason `execve` fails is because `%rdx` is `name`, which is a pointer to `"/bin/sh"`, and so `execve` tries to dereference `0x0068732f6e69622f` and returns `-EFAULT`.
# And since we don't know the heap address, we can't put a valid pointer there!

# Wait! Does `%rdx` HAVE to be a pointer to a NULL array?
# Yes, `envp` must be an array of pointers ending with a NULL pointer.
# If `name[0]` is a pointer, `execve` will read it.
# Can we put a VALID pointer at `name[0]`?
# We have libc leak! We know `libc_base`!
# We can put `libc_base + offset` at `name[0]`, where `offset` points to a `NULL` pointer!
# A NULL pointer in libc is just 8 bytes of zeros.
# There are many 8 bytes of zeros in libc! (e.g. `libc_base + 0x219000` bss).
# IF `name[0]` = `p64(libc_base + 0x219000)`, then `execve` reads `name[0]` as the first envp pointer.
# It dereferences `libc_base + 0x219000` and reads `NULL`.
# So `envp` is valid (empty)!
# BUT THEN `name` (the filename) is the string representation of `p64(libc_base + 0x219000)`!
# As a string, it will be `"\x00\x90\x21..."` if `libc_base` ends in 000.
# If it starts with `\x00`, then the filename is `""` (empty string).
# `execve` will try to execute `""`, which fails with `-ENOENT`!

# So the FIRST byte of `p64(libc_base + offset)` must NOT be `\x00`!
# AND `libc_base + offset` must point to `NULL` (8 bytes of zero)!
# So we need `libc_base + offset` to NOT have `\x00` in its least significant byte!
# But `libc_base` ends in `000`!
# E.g. `0x7fa377243000`.
# If `offset = 0x219010`, `libc_base + offset = 0x7fa37745c010`.
# The LSB is `0x10`. The next byte is `0xc0`.
# As a string, this is `"\x10\xc0\x45\x77\xa3\x7f"`.
# This is a string of length 6.
# If we create a file named `\x10\xc0\x45\x77\xa3\x7f` in the current directory and make it an executable shell script, `execve` WILL execute it!
# BUT we CANNOT create files in the current directory remotely because we don't have a shell!
# Unless `gets` allows us to? No, `gets` just writes to the heap buffer.
