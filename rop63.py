# Is there a function in libc that executes a shell command and does NOT use `movaps`?
# E.g. `system` uses `do_system` which uses `movaps`.
# What about `wordexp`? It might.
# What about `popen`? It calls `_IO_new_popen`, which does `malloc` (might use movaps).
# What about `execl`?
# In libc 2.35, `execl` takes arguments from the stack.
# `execl` uses variadic arguments, so it might dump registers to the stack.
# Does `execl` use `movaps`?
