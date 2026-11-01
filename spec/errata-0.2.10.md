# Binding interpretations of accepted dialect 0.2.10

Published with draft 0.2.12, 2026-11-01. Accepted text at `023f5a771a814270634db3be9cfde88ded69f975`, spec SHA-256 `d4f3c1a88391cc147f8c8fa4f80f82852e3ebe6f880610fc16cd5151f33d7206`, is unchanged; consumer pins remain valid. These interpretations resolve ambiguity in that text; new 0.2.12 ABIs/accuracy requirements are identified separately and are not retroactive ABI changes.

## mkb — §§5.2, 7.2, 12.2 N0

**N0 and resolution order.** Before testing the forwarding-thunk predicate or freezing candidates, the plugin MUST apply the N0 passes of §12.2 to the virtual device bodies used by S2; §7.2 resolution then uses those bodies, and §7.3 hashes their materialised closures.

The plugin MUST retain A(S) for every original source function or alias whose address reaches the region operand, dispatching that address to its post-N0 resolved candidate even when N0 removes the forwarding call; a declaration remaining after N0 is still F(8), but an intrinsic call removed by N0 MUST NOT turn its containing defined body into an external candidate.
