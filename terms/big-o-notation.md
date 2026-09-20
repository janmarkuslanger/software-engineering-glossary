---
name: Big O Notation
sources:
  - title: "Knuth, D. E. — Big Omicron and Big Omega and Big Theta (1976)"
    url: https://dl.acm.org/doi/10.1145/1008328.1008329
  - title: "Cormen et al. — Introduction to Algorithms, Chapter 3"
    url: https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/
---

A notation for the **upper bound on how an algorithm's cost grows** as its input grows.
`O(n)` means runtime grows at most proportionally to the input size, `O(n²)`
quadratically, `O(log n)` logarithmically.

Big O deliberately discards constants and lower-order terms: it describes scaling
behaviour, not absolute speed. An `O(n²)` algorithm can easily beat an `O(n log n)`
one on small inputs.

## Common classes

| Notation | Growth | Typical example |
| --- | --- | --- |
| `O(1)` | constant | hash map lookup |
| `O(log n)` | logarithmic | binary search |
| `O(n)` | linear | scanning a list |
| `O(n log n)` | linearithmic | comparison sorting |
| `O(n²)` | quadratic | nested loops over the same list |
