# Babyheap Write-up

## Introduction
The `babyheap` challenge is a classic binary exploitation puzzle designed around the concept of a "Capture The Flag" (CTF) game. In this challenge, our goal is to gain remote control over a server application written in C++ and instruct it to read a secret "flag" file for us.

The flag format is typically `grey{...}`, and retrieving it proves we successfully hacked the application.

## Step 1: Analyzing the Vulnerable Program
The first step in any binary exploitation challenge is understanding how the program works and looking for loopholes. By examining the source code (`babyheap.cpp`), we discover the program allows users to create virtual "Monkeys" and "Greycats".

Both of these objects are stored in the computer's memory (specifically, an area called the "heap").
Here is a simplified view of a `Greycat`:
```cpp
class Greycat {
public:
    int legs = 4;
    char name[32];
    void (*speak)(char[]) = meow; // A function pointer that makes the cat "speak"
};
```
The vulnerability lies in how the program asks for a name:
```cpp
cin >> name;
```
This single line of code tells the program to read what the user types and store it in the `name` box, which is meant to hold only 32 characters. However, `cin >> name;` does not actually enforce a limit of 32 characters! It will keep reading until the user presses space or enter.

If we type a name longer than 32 characters, the text spills over (overflows) out of the `name` box and overwrites the next item in memory. The very next item in memory is the `speak` function pointer—a signpost that tells the program which action to execute when we command the cat to talk.

If we overwrite this signpost, we can trick the program into executing *any* function we choose!

## Step 2: The Location Problem (Leaking Libc)
To trick the program into executing a different function (like opening a command shell to read our flag), we need to know exactly where that function is located in the computer's memory.

Modern computers use a security feature called **ASLR** (Address Space Layout Randomization). Every time the program runs, it shuffles the locations of all its internal libraries (like `libc`, the standard library containing useful functions) so hackers can't easily guess where things are.

Fortunately, the developers left a debugging backdoor in the code. By entering the secret menu option `6767`, the program prints out the exact memory address of `malloc` (a common function inside `libc`).
Once we know where `malloc` is, we can mathematically calculate the exact starting location of the entire `libc` library. With that base location, we can find the address of *any* function we want.

## Step 3: Finding the Right Exploit Function
Usually, hackers try to overwrite the function pointer to point to `system`, a function that can run command-line scripts. We want to execute `/bin/sh` to give us a command shell.

However, `system` in modern versions of Ubuntu comes with strict requirements. Specifically, it uses advanced processor instructions (like `movaps`) that demand the computer's memory stack be perfectly aligned to 16-byte boundaries. Because of how the program was written, our stack is misaligned by 8 bytes at the moment the cat tries to "speak". If we use `system`, the program crashes instantly.

Additionally, the program is protected by Intel CET (Control-flow Enforcement Technology), meaning we can only jump to certain approved starting points (instructions called `endbr64`).

We need a function that:
1. Gives us a shell or executes our command.
2. Doesn't crash due to the 16-byte alignment rule.
3. Is an approved starting point (`endbr64`).

## Step 4: The `execl` Magic Trick
After examining the `libc` library, we find another function called `execl` that perfectly fits our criteria. `execl` doesn't suffer from the strict memory alignment issues that `system` does.

When the program tells the cat to speak, it essentially does this:
```cpp
greycat->speak(greycat->name);
```

By overwriting the `speak` signpost with the address of `execl`, we effectively run:
```cpp
execl(greycat->name, 0);
```

If we make the cat's name `/bin/sh`, the program will execute `/bin/sh` (a command shell). The `0` acts as a clean end-of-list marker for `execl`.

## Step 5: Executing the Attack
We put it all together into an automated Python script:
1. Connect to the server.
2. Select option `6767` to get the secret memory leak.
3. Calculate the address of `execl`.
4. Create a new cat, but give it a massively oversized name.
5. The name starts with `/bin/sh` followed by a bunch of 'A's to fill up the 32 characters, and ends with the exact memory address of `execl`.
6. We command the cat to speak.

Instead of meowing, the program executes `execl("/bin/sh")` and opens a shell.
From there, we simply send the command `cat flag.txt` to read the hidden file.

**Flag Captured:** `grey{b4by_st3p5_1n_babY_h34P!}`
