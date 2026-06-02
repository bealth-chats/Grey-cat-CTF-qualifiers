# Wow! I solved it!
# `execl` was the magic function!
# Because `%rdi = name`, `%rsi = 0`.
# `execl` sees `%rdi = "/bin/sh\x00"` and `%rsi = NULL`.
# So it constructs `argv = [NULL]` and `envp = environ`.
# And then it calls `execve` which succeeds because `environ` is valid and `argv` is valid!
# And it doesn't use `movaps` because it doesn't do complex register saving/floating point operations!
# This completely bypasses the `movaps` issue AND the `envp` garbage pointer issue!
