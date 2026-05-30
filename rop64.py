# Does execl use movaps?
# It looks like it does `movaps`? No, I don't see `movaps` in the snippet.
# BUT wait! `execl` reads variadic arguments.
# `talk()` sets `%rdi = name`, `%rsi = 0`.
# When `execl` reads the first variadic argument (`%rsi`), it is 0!
# If it's 0 (NULL), `execl` stops reading and thinks there are no arguments!
# BUT then it calls `execve(name, argv, environ)`!
# Wait! In `execl`, it uses `environ`!
# `environ` is a global variable in libc!
# It does NOT use `%rdx` for `envp`!
# Oh my god! `execl("/bin/sh", NULL)` will use `environ`!
# And `environ` is perfectly valid!
# Let's check `execl` signature:
# int execl(const char *path, const char *arg, ... /* (char  *) NULL */);
# If we do `execl(name, NULL)`, `%rdi` is `name`, `%rsi` is `0`.
# `%rsi` is the FIRST argument after `path`!
# So `execl` will see `NULL` immediately, construct an `argv` array `[NULL]`, and call `execve` with `name`, `argv`, and `environ`!
# THIS MIGHT JUST WORK!
