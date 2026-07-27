# Loop Detection in DPDA ε-Transition Simulation

## 1. Setup

A **Deterministic Pushdown Automaton (DPDA)** is a tuple $M = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$ where $Q$ is a finite set of states, $\Sigma$ is the input alphabet, $\Gamma$ is the stack alphabet, $\delta$ is the (partial, deterministic) transition function, $q_0$ is the start state, $Z_0 \in \Gamma$ is the initial stack symbol, and $F \subseteq Q$ is the set of accepting states.

An **ε-transition** $\delta(q, \varepsilon, A) = (q', \gamma')$ moves the machine from state $q$ to $q'$, replacing the top-of-stack symbol $A$ with string $\gamma'$, **without consuming any input**. A chain of ε-transitions may run for arbitrarily many steps between two input reads — or forever.

The question we must answer algorithmically is:

> **Does the DPDA halt on a given input, or does it loop forever on ε-transitions?**

---

## 2. The Loop Detection Rule

The simulator tracks, for each **configuration key** $c = (\text{state},\ \text{stack top},\ \text{input index})$, two values:

- $\text{min\\_ever}(c)$: the minimum stack length observed across all visits to $c$ so far.
- $\text{last\\_len}(c)$: the stack length at the most recent visit to $c$.

Each time an ε-transition is about to be taken from configuration $c$ with current stack length $\ell$:

1. If $c$ has not been visited before: record $(\ell,\ \ell)$ and continue.
2. If $c$ has been visited before:
   - If $\text{min\\_ever}(c) \geq \text{last\\_len}(c)$: **declare a loop and reject**.
   - Otherwise: update $\text{min\\_ever}(c) \leftarrow \min(\text{min\\_ever}(c),\ \ell)$ and $\text{last\\_len}(c) \leftarrow \ell$, and continue.

When a **real input symbol** is consumed, `input_index` increments, so all configuration keys at the new index are fresh — the loop detection state resets naturally across input reads without any explicit clearing.

---

## 3. Correctness

### 3.1 Soundness

**Claim:** If the loop condition triggers, the machine truly loops forever.

This part is not that hard — left to the reader.

---

### 3.2 Completeness

**Claim:** If the machine loops forever on ε-transitions, the algorithm will eventually declare a loop.

**Proof.**

Suppose $M$ enters an infinite chain of ε-transitions with the input index fixed at $i$, producing an infinite sequence of configurations. Call a config key $c = (q, A, i)$ **good** if it appears **infinitely often** in this sequence; otherwise call it **bad**.

Since the set of all config keys has size at most $|Q| \times |\Gamma|$, which is finite, by the **Pigeonhole Principle** at least one key must be good. Since bad keys each appear only finitely many times, there is some point in the execution after which **every** config key visited is good. Discard everything before that point; from here on the sequence visits only good keys.

Among all configurations in this suffix, let $\langle q^* , \gamma^* \rangle$ be the one with the **shortest stack** (break ties arbitrarily). Let $A^* = \text{top}(\gamma^*)$ and $\ell^* = |\gamma^*|$. Its config key $c^* = (q^* , A^* , i)$ is good, so it appears infinitely often. Let visit $j$ be the visit to $c^*$ where the stack length is $\ell^*$, and let visit $j+1$ be any subsequent visit to $c^*$.

**Claim: the stack never goes below $\ell^*$ between visits $j$ and $j+1$.**

Suppose for contradiction the stack went below length $\ell^*$ at some point $t$ strictly between visits $j$ and $j+1$. Let $c_t = (q_t, A_t, i)$ be the config key at time $t$. Since $t$ is in the suffix where only good keys are visited, $c_t$ is good — meaning it recurs infinitely often, so it is a configuration with a stack shorter than $\ell^*$ that appears infinitely often. This contradicts the choice of $\langle q^* , \gamma^* \rangle$ as the configuration with the **shortest stack** in the suffix. ↯

Therefore the stack never falls below $\ell^*$ between visits $j$ and $j+1$, so:

$$\text{min\\_ever}(c^*) \geq \ell^* = \text{last\\_len}(c^*)$$

and the algorithm **declares a loop** at visit $j+1$. $\blacksquare$
