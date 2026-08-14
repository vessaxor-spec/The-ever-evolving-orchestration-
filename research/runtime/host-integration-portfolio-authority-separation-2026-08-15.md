# Host Integration Portfolio Authority Separation Research

**Date:** 2026-08-15  
**Status:** executable non-normative research  
**Scope:** process-local separation between host-owned portfolio/task-admission authority and TEO orchestration of an explicitly admitted task

## Question

Can an external host admit one exact task into TEO without giving TEO authority to select, enqueue, prioritize, cancel, revoke, dequeue, or synthesize other host work?

## Research claim

A conformant host integration can keep portfolio and task-admission authority on the host side while exposing to TEO only a bounded claim/revalidation gateway for one exact host-issued task admission.

The research authority binds an admission to:

- host portfolio identity;
- exact admission identity;
- exact task identity;
- SHA-256 digest of the exact admitted task payload;
- host-owned admission revision; and
- an HMAC-bound host authorization token.

TEO can claim that exact admission once and revalidate the resulting task session. The TEO-facing gateway exposes no operation for queue creation, task selection, admission, prioritization, cancellation, revocation, or portfolio inspection.

## Separation from Task Intent & Action Authority

This slice is earlier than request/action-authority interpretation.

The boundary is:

```text
host/user portfolio and task admission authority
  -> exact admitted task
  -> TEO orchestration
  -> request/action authority and other applicable controls
  -> host/TEO execution-authority intersection
  -> exact action envelope
```

This research does not determine what side effects an admitted request authorizes. The Task Intent & Action Authority research remains responsible for that separate question.

## Adversarial cases

The test matrix includes:

- exact host-issued admission positive control;
- a queued and otherwise routable task with no host admission;
- TEO request injection of priority or queue position;
- TEO request injection of cancellation or sibling-admission fields;
- attempted `dequeue_next_task` operation;
- forged host admission token;
- admission-identity mutation;
- admitted-task identity mutation;
- post-admission task-payload mutation;
- sibling admission used against another task;
- admission replay that would duplicate TEO work;
- concurrent duplicate admission claims;
- host cancellation after TEO claim;
- host admission revocation after TEO claim;
- host reprioritization after admission, proving priority remains host-owned rather than part of TEO execution authority;
- absence of portfolio mutation methods on the conformant TEO-facing gateway;
- sibling cancellation without widening or revoking the current admitted task;
- cross-portfolio grant reuse;
- unknown widening fields in the host grant;
- task substitution during session revalidation;
- session binding tamper; and
- duplicate host admission for the same already-admitted task.

## Authority boundary

This slice is research only. It does not:

- create a normative host-admission schema;
- give TEO backlog, product-priority, queue, scheduling, or portfolio authority;
- interpret natural-language request intent or action authority;
- authorize any host action;
- change routing, risk, specialist selection, capability resolution, model/provider selection, retry, recovery, verification, finalization, or qualified-human authority;
- widen live execution;
- authorize the staged `documentation` candidate;
- prove resistance to a compromised host process that ignores the conformant gateway; or
- define distributed queue, scheduler, or admission semantics.

A task being routable, low risk, capability-valid, or technically executable is not admission authority.

## Residual limits

This research does not close:

- remote or distributed host-admission authenticity;
- durable admission/revocation state across restart;
- compromised-host bypass;
- production scheduler and queue integration;
- tenant/account/credential binding;
- distributed duplicate-work prevention;
- request/action-authority interpretation;
- dynamic admission policy or automated portfolio optimization; or
- provider-backed execution evidence.

## Roadmap relationship

This slice targets Host Integration promotion gate 15, **portfolio-authority separation**, which currently has a research principle but no executable promotion evidence.

A passing process-local slice would support only the conformant boundary that TEO receives explicitly admitted work and cannot widen that into host portfolio authority through the exposed path. It would not make the Host Integration Contract normative or change the canonical live-execution priority.
