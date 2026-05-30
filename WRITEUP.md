# GreyCat Game - CTF Write-up

**Challenge Description:** "This game looks familiar... but something is a little off(?)"

## Overview
The challenge presents us with a browser-based endless runner game, very similar to the famous Google Chrome T-Rex dinosaur game, but starring a cat instead. Since the challenge description hints that "flags rarely sit in the foreground," our job is to look under the hood and find where the flag is hiding.

## Step 1: Investigating the Game Code
To figure out how the game works, we can look at the underlying files that run it. The main file to check is usually the JavaScript file because it contains the game logic. In this case, there's a file called `game.js`.

By looking through `game.js`, we can spot a few interesting things:
1. **Bootstrap API**: When the game starts, it makes a request to `/api/bootstrap`. This gives the game a `fastPhaseScore` (around 2250) and a special session cookie to keep track of our progress.
2. **Run API**: As we play the game, it constantly checks in with the server by making requests to `/api/run` to report our score and "tick" (how long we've been running). The server verifies that our score is increasing at a normal rate.
3. **Ghost API**: The most interesting part! If our score goes above the `fastPhaseScore` (which is quite high and takes a while to reach legitimately), the game enters a "fast phase". During this phase, it starts requesting `/api/ghost` to show "spectral fragments" or "ghosts" in the background of the game.

## Step 2: Uncovering the Ghosts
Looking closely at the `revealFlagFragment` function in `game.js`, we can see what these "ghosts" actually are. When the game requests a ghost, the server returns an encrypted text block (called a "stamp").

The game then calls a function called `decodeStamp` to decrypt this block:
```javascript
function decodeStamp(stamp, traceId) {
  // ... decryption logic ...
}
```
This function uses some math based on a "traceId" provided by the server to unlock the encrypted text and reveal a hidden message. These hidden messages are pieces of our flag!

## Step 3: Automating the Process (Writing a Solver)
Playing the game all the way to a score of 4000 without crashing is difficult. Fortunately, since we know exactly how the game talks to the server, we don't have to play it manually. We can write a script that pretends to be a very good player.

Our script (which you can find in `solve.js`) does the following:
1. It asks `/api/bootstrap` to start a new game session.
2. It uses a loop to rapidly send `/api/run` requests, tricking the server into thinking we are playing and gaining score over time.
3. Once our fake score crosses the `fastPhaseScore`, it starts asking the server for ghosts from `/api/ghost`.
4. It takes the encrypted stamp from the server, runs the exact same `decodeStamp` function the game uses, and prints out the hidden text.

## The Solution
When we run our script, the server believes we have reached an incredibly high score and starts sending us the ghost fragments one by one:
- `grey{th3_`
- `trex_`
- `rep1ac3d_`
- `by_a_`
- `gr3y_`
- `cat}`

Putting them all together, we get the complete flag!

**Flag:** `grey{th3_trex_rep1ac3d_by_a_gr3y_cat}`
