---
name: Dependency Injection
sources:
  - title: "Fowler, M. — Inversion of Control Containers and the Dependency Injection pattern"
    url: https://martinfowler.com/articles/injection.html
  - title: "Martin, R. C. — The Dependency Inversion Principle"
    url: https://web.archive.org/web/20110714224327/http://www.objectmentor.com/resources/articles/dip.pdf
---

A component receives its dependencies it needs **from the outside** instead of
constructing or locating them itself.

```python
# Reaches out for its dependency — hard to test, hard to reuse.
class Report:
    def __init__(self):
        self.db = PostgresClient(os.environ["DSN"])

# Dependency injected — the caller decides what "storage" is.
class Report:
    def __init__(self, storage):
        self.storage = storage
```

The injected version can be run against an in-memory double in tests and against
Postgres in production without changing a line of `Report`.

