---
name: Memoization
sources:
  - title: "Michie, D. — Memo Functions and Machine Learning (Nature, 1968)"
    url: https://www.nature.com/articles/218019a0
  - title: "Python docs — functools.lru_cache"
    url: https://docs.python.org/3/library/functools.html#functools.lru_cache
---

Caching the result of a function per argument set, so a repeated call with the same
arguments returns the stored result instead of recomputing it.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

Memoization is only correct for **pure** functions: same input, same output, no side
effects.
