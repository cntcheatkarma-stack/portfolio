# Logic Lights

**Status:** Complete (playable)
**Category:** Educational game
**Language:** HTML, CSS, JavaScript (single file, no dependencies)

## Summary

A small ASCII-art game for learning logic gates. You get a random tree of 3 to 5 gates. Flip the inputs so the OUT light turns on, then press Check. Checking reveals the light on every gate, so a wrong answer shows where the signal stops.

```
[A:1]-+
      +-[AND]-(*)-+
[B:1]-+           |
                  +-[OR]-(*)-+
[C:0]-------------+          |
                             +-[AND]-(*)--> OUT
[D:1]------------------------+
```

## Play

Open `index.html` in a browser. There's nothing to install or build.

- Click an input, or press its letter, to flip it
- Enter: check
- N: new circuit

## Levels

| Level | Gates | Gate types |
|-------|-------|------------|
| 1-2   | 3     | AND, OR |
| 3-4   | 4     | adds XOR, NOT |
| 5+    | 5     | adds NAND, NOR; one input can feed two branches |

## Design notes

- **Puzzle generation:** builds a random gate tree, then checks every possible input combination. A puzzle is kept only if it's solvable, the winning combinations are no more than half of all combinations (so it isn't a giveaway), and the starting state is a losing one.
- **Hidden lights:** gate outputs stay hidden as `(?)` until you check, so you have to reason it out instead of flipping inputs at random.
- **Testing:** the generator and the ASCII renderer were tested headlessly in Node on 3,000 random circuits. Each one starts unsolved, has the right number of gates for its level, and draws every gate.
