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

The current specialist workers are defined in [`workers.yaml`](workers.yaml).

## Dispatch hierarchy

```text
Mission Control
  |
  v
Core or Specialist Team
  |
  v
Worker
  |
  v
Implementation
```

Implementation preferences may change as evidence and model availability change. Worker responsibilities should remain stable unless the work domain itself changes.
