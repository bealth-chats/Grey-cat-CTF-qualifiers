# What if we overwrite `speak` with `_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc` (operator<< for strings)?
# Or maybe something that executes system without movaps.
# In `libc_2.35.so`, there is `wordexp`. Let's see if we can use it.
# We have a format string vulnerability! We tested `test_printf.py` and it WORKED!
# `1. Create monkey\n2. Create greycat\n3. Make greycat talk\n`
# Wait, did it work?
# The output was: `b'1. Create monkey\n2. Create greycat\n3. Make greycat talk\n'`
# That's just the menu printing over again!
# Where was the `|%p|...` output?
# Ah! `printf` failed!
# Let me look closely: `test_printf.py` sent the payload and then waited for output.
# If `printf` succeeded, it should have printed `|0x...|0x...`.
# But the output was ONLY the menu!
# Why? Because `printf` expects `%rdi` to be a valid format string pointer.
# `%rdi` was `name`. And `name` STARTED with `|%p|%p...`.
# So `printf("|%p|%p...")` SHOULD have printed something!
# But it didn't! Why?
# Maybe `printf` crashed! And since `test_printf.py` caught the exception or closed, it only printed what was before the crash!
# Let's check locally! I did test locally and got `SIGSEGV` in `test_printf.py`!
# Ah! `printf` crashed due to `movaps` as well!
# I said this earlier: "printf ALSO uses movaps and requires a 16-byte aligned stack! That's why it segfaults!"
# Yes.
