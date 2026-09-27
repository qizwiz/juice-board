# Engineering notes

The instrument is small on purpose. What is unusual about it is where the arithmetic lives and how it is
checked.

## The pricing kernel is a proof first

The fee and edge arithmetic is written in **Lean 4** over integer cents, with the venue fee models as
definitions and the fixtures (including the exact fee table rows above) checked by `decide`. The same
source compiles to C. Measured on this laptop: **273–423 ns per verdict** with fixed parameters, **1.39 µs**
when the seven tunable parameters are read live. The Python reference implementation of the same verdict
takes about 68 µs.

Theorems worth having: the Kalshi ceiling implies a minimum fee of one cent (so a size floor exists for
every tuning), the empty book prices to *none*, and the two-leg all-in cost fixtures agree between the Lean
kernel and the Python instrument to the cent.

## Parameters are tunable while it runs

The seven parameters (Kalshi fee base, Kalshi fee multiplier, Polymarket fee rate, the Kelly fraction, the
dust threshold, the carry hurdle and the divergence-loss assumption) live in a 64-byte memory-mapped block
guarded by a **seqlock**. The writer takes a file lock; readers retry on a torn
sequence. The lock was checked in **TLA+**: the unlocked two-writer model produces a torn-read counter-example
in 12 states; the locked model exhausts 1,701 states with no error.

## Latency, measured

From a home connection in Texas, to Kalshi: a fresh HTTPS connection costs 160–220 ms (70–145 ms of it
TCP + TLS); a reused connection costs **70 ms**, which is the round trip. To Polymarket, a pair fetch that
pays its handshakes runs about 270–350 ms at the median. One full scan of 34 pairs, with connections kept
alive, completes in about **1.6 s** of wall time; the instrument runs one every 20 s. The venues' websockets
are the push path; the poll is the floor.

## What the instrument refuses to do

- Price a partial fill as a fill: a book too thin for the minimum size returns *none*.
- Report a rate without its denominator: every gate prints `k / N`.
- Trade. There is no order-placement code path.
