# Write-up: Filter Flag

In this challenge, we are connected to a server that has a secret message, known as a "flag". Our goal is to retrieve this flag.

## 1. Understanding the Game
When we connect to the server, it gives us the secret flag, but it is **encrypted** (scrambled so we can't read it). The server then lets us play a game: we can send it any scrambled message, and it will try to decrypt it and show us the result.

However, there are two catches:
1. We cannot ask it to decrypt the exact same encrypted flag it just gave us. It checks for this and will say "lol no".
2. It breaks the message into small chunks (called blocks). If a chunk turns into unreadable gibberish after being decrypted, the server will hide it and show `????????????????` instead. It only reveals chunks that look like normal text.

## 2. Finding the Weakness
The encryption method the server uses is a custom version of something called "PCBC mode". Think of it as a chain: to decrypt chunk #3, the server relies on the math from chunk #1 and chunk #2.

Because of a flaw in the way the math (specifically, the "XOR" operation) is set up, the order in which we process the chunks doesn't completely matter. If we **swap** the first two chunks of the scrambled message, the math gets messy for chunk #1 and chunk #2, but perfectly fixes itself by the time it reaches chunk #3!

This means chunks #3, #4, and #5 will decrypt perfectly into the original, readable flag, while chunks #1 and #2 will be hidden as `????????????????`.

## 3. Getting the First Half of the Flag
We need to read the first few chunks of the flag. To do this, we can take the original encrypted flag and make a tiny change to the **very last chunk**.

Because of the chain reaction, changing the last chunk only breaks the very end of the message. The first few chunks (chunks #1, #2, #3, and #4) are completely unaffected and will be decrypted perfectly by the server! The last chunk will be garbled and hidden.

When we send this to the server, it responds with:
`grey{7c0c6a199cda0a96b55e74c5e1394284655e623c68f72ba59e4eb9fdb4_` (followed by hidden text)

## 4. Getting the Second Half of the Flag
Next, we need the end of the message. To do this, we take the original encrypted flag and **swap the first and second chunks**, just like we realized we could do earlier.

When we send this modified message to the server, it garbles the beginning but perfectly decrypts the end!
It responds with:
`????????????????????????????????94284655e623c68f72ba59e4eb9fdb4_W4h_uR_Q_gUd_4h}`

## 5. Piecing it Together
Now we have two pieces of the puzzle:
- **Piece 1:** `grey{7c0c6a199cda0a96b55e74c5e1394284655e623c68f72ba59e4eb9fdb4_`
- **Piece 2:** `94284655e623c68f72ba59e4eb9fdb4_W4h_uR_Q_gUd_4h}`

By overlapping the parts that are the same, we can reveal the full flag!

**Final Flag:**
`grey{7c0c6a199cda0a96b55e74c5e1394284655e623c68f72ba59e4eb9fdb4_W4h_uR_Q_gUd_4h}`
