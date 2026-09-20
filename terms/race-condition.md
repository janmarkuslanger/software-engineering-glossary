---
name: Race Condition
sources:
  - title: "Lamport, L. — Time, Clocks, and the Ordering of Events in a Distributed System"
    url: https://lamport.azurewebsites.net/pubs/time-clocks.pdf
  - title: "CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization"
    url: https://cwe.mitre.org/data/definitions/362.html
---

A bug where the **result depends on the timing of concurrent operations**. Two threads read the same values, both add ten, and one of the two updates is silently lost.

Race conditions are hard to find because the failing interleaving may occur once in a
million runs — and reliably on the production machine with more cores than a local laptop.

## Defences

- Do not share mutable state; pass messages or copies instead.
- Where sharing is unavoidable, guard it with a lock, an atomic operation or a
  transaction.
- Let the database decide: unique constraints and conditional updates (`WHERE
  version = ?`) turn a race into a rejected write.
