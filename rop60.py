# Let's consider another approach:
# What if we overwrite `speak` with `gets` to read into `name`.
# Then we overwrite `speak` with `main`.
# Wait, I said we couldn't because it preserves stack alignment.
# What about a gadget that calls `execve`?
# In libc 2.35, `system` uses `movaps`, `printf` uses `movaps`.
# Does `puts` use `movaps`?
# Does `puts` require 16 byte alignment?
