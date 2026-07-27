# DPDA-simulator
Deterministic Pushdown Automata (DPDA) simulator with ε-transition loop detection.

I put this project here because I couldn't find a clean, readable implementation of DPDA simulation anywhere — especially one that correctly handles **ε-transition loop detection**, which is the interesting engineering and theoretical problem here.

---

## Features

### DPDA Simulator
- Supports both **final-state** and **empty-stack** acceptance modes
- Traces input strings step by step with full stack display
  
---

## Usage

**Transition format:** `state_from  input_char  stack_top  state_to  stack_write`

! Use `eps` for ε-transitions (no input read) or for writing nothing to the stack (pop only).

---

## The Interesting Part: ε-Loop Detection

A DPDA with ε-transitions can loop forever without ever reading input — the stack just keeps growing or cycling. Detecting this is non-trivial because the stack is unbounded.

The key insight, and the proof that the detection is correct, is in [`PROOF.md`](PROOF.md).

The short version: track, for each configuration `(state, stack_top, input_index)`, the minimum stack length ever seen and the stack length at the last visit. If the stack never shrank between two visits to the same configuration, the machine is in an infinite loop.

---
