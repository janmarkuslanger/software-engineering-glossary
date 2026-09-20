---
name: Refactoring
sources:
  - title: "Fowler, M. — Refactoring: Improving the Design of Existing Code"
    url: https://martinfowler.com/books/refactoring.html
  - title: "Fowler, M. — Refactoring catalog"
    url: https://refactoring.com/catalog/
---

Changing the internal structure of code **without changing its observable behaviour**,
in small steps, to make it easier to understand and cheaper to change.

The behaviour-preserving part is what separates refactoring from rewriting. It is also
what makes a test suite a precondition rather than a nice-to-have: without one, you
cannot tell a refactoring from an accident.