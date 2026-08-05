## Problem and outcome

<!-- What problem does this solve, and what is now observably different? -->

## Scope

- Affected services/packages:
- API or wire-contract changes:
- Database or migration changes:
- Environment or deployment changes:
- Deliberately out of scope:

## Implementation notes

<!-- Explain decisions reviewers cannot infer easily from the diff. Confirm that the agent -> MCP -> backend boundary is preserved when relevant. -->

## Validation

<!-- List exact commands and results. Do not report `npm test` as functional coverage while its workspace scripts remain placeholders. Identify any skipped external or credential-dependent probe. -->

```text
command: result
```

## User-visible evidence

<!-- Add before/after screenshots or a recording for UI changes. Remove personal data, credentials, and private host details. Delete this section when not applicable. -->

## Risk and rollout

- Failure modes:
- Rollout/compatibility plan:
- Rollback plan:
- Monitoring or post-deploy verification:

## Checklist

- [ ] The change is focused and preserves unrelated work.
- [ ] Strict frontend types and service boundaries remain intact.
- [ ] API-shape changes include schemas, adapters/types, MCP callers, and focused tests.
- [ ] Database changes are new migrations beside the owning datastore and were rehearsed on a disposable/restored copy.
- [ ] No secret, private endpoint, authorization header, or sensitive log output was added.
- [ ] Current documentation and examples were updated; superseded point-in-time material was archived.
- [ ] Relevant lint, type, build, test, container, and manual checks are listed above.
- [ ] Known limitations and deferred work are explicit.

See the [testing guide](../docs/testing.md) and [contribution guide](../CONTRIBUTING.md).
