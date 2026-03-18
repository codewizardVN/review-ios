[English](./ReleaseProcess.md) | [Tiếng Việt](./ReleaseProcess.vi.md)

[← Senior Topics](./README.md)

# Release Process

## What A Senior Should Cover

- scope control and release criteria
- feature flags and kill switches
- QA, smoke tests, and monitoring
- rollback or mitigation plans

## Typical Flow

1. Freeze scope for the release candidate.
2. Run targeted regression checks on high-risk areas.
3. Verify analytics, logging, and crash reporting are ready.
4. Roll out gradually if possible.
5. Monitor crashes, key funnels, and backend health.

## Practice Questions

- What blocks a release for you?
- How do you reduce release risk when the deadline is fixed?

## Senior Take

Releasing is an operational discipline, not just pressing a button in App Store Connect. The best answers balance delivery speed with guardrails that let the team recover quickly.

## Exercise

Your team must ship a payments update before a marketing campaign. Build a release checklist with pre-release checks, rollout strategy, monitoring signals, and stop-ship criteria.
