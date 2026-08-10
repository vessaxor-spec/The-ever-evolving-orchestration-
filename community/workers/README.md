# TEO Workers

Workers are stable responsibility profiles owned by teams. A worker is not a model.

Each worker defines:

- Mission
- Owning team
- Responsibilities
- Required capabilities
- Preferred implementations
- Fallbacks
- Verification requirements
- Escalation conditions

The stable worker profiles are defined in [`workers.yaml`](workers.yaml).

Active additive worker definitions are under [`extensions/`](extensions/). The reference router loads an explicit governed list of those files; it does not discover arbitrary worker YAML by directory traversal.

Superseded worker staging records belong under [`docs/history/activation/`](../../docs/history/activation/), not in the active worker namespace.

## Specialist bindings

A specialist narrows a worker to a particular domain without replacing the worker or owning team.

The public specialist roster was created by **Sylvester Roxas** and is defined in [`community/specialists/`](../specialists/).

The machine-readable bindings are maintained in [`community/specialists/specialists.yaml`](../specialists/specialists.yaml).

## Dispatch hierarchy

```text
Mission Control
  |
  v
Core Team
  |
  v
Worker
  |
  v
Optional Specialist
  |
  v
Capability
  |
  v
Implementation
  |
  v
Verification
```

Implementation preferences may change as evidence and model availability change. Worker responsibilities and specialist authority boundaries should remain stable unless the work domain itself changes.
