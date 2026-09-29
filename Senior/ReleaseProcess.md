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

## Practice Question Answers

### What blocks a release for you?

I block a release when an issue harms users or the business and cannot be mitigated after shipping; small issues with a workaround become known issues and we still ship. Stop-ship criteria should be agreed in advance with product and QA, not decided by gut feeling at the last minute.

The criteria I usually use:

- A crash or hang in a core flow (launch, login, checkout), or a release candidate crash-free rate below the threshold compared with the previous version.
- Loss or corruption of user data, or a failing migration.
- Money-related bugs: wrong prices, double charges, purchases that can't be restored.
- Security or privacy problems: tokens leaked into logs, data collected without being declared in the privacy manifest or privacy label.
- A risky feature without a feature flag or kill switch to turn it off.
- Missing operational pieces: dSYMs not uploaded, analytics for key funnels not working.

Things not worth blocking: minor UI glitches, bugs in features currently switched off by a flag, bugs that already existed in the previous version and are no worse.

When I block, I tell product clearly: what the problem is, how many users it affects, and the options (fix and slip X days, or turn the feature off and ship on time). Trade-off: blocking too easily makes the team lose its rhythm, and the next release becomes bigger and riskier; so the decision must be based on severity and on how fixable it is after shipping.

### How do you reduce release risk when the deadline is fixed?

When the deadline can't move, I reduce risk by cutting scope and increasing the ability to turn things off or recover — not by working overtime and skipping tests.

Concretely:

- **Freeze scope early:** do what matters most for the deadline first; push unfinished parts behind a flag or into the next release.
- **Feature flags with a remote kill switch:** the code ships but is only enabled once verified, and can be turned off without a new build.
- **Code freeze and a release branch a few days early:** only approved fixes go in.
- **Early TestFlight** for internal testers and a beta group; regression testing focused on changed areas and revenue flows.
- **Submit to App Review early** to have buffer, and choose manual release to go live on the intended day.
- **Phased release** on the App Store, watching crashes and funnels, pausing on bad signals.
- **A hotfix plan ready in advance** and someone on call for the first days.

Trade-off: cutting scope needs product's agreement. I present it as a clear choice: ship full scope with risk X, or ship the core on time and the rest a week later. Last-minute crunch usually adds bugs rather than reducing risk.

## Interview Traps

### "The new version is badly broken after going live. How do you roll back?"

**Common wrong answer:** "Roll back to the previous build in App Store Connect." The App Store has no rollback for users who have already updated.

**Better answer:** Users who installed the broken build keep it until a new one arrives. The real tools are: turning the feature off via a kill switch or remote config, fixing on the server side where possible, pausing the phased release to reduce auto-updates, and shipping a hotfix with a new build number, possibly requesting an expedited review. Note: a version that has been released (for example 2.3.0) no longer accepts new builds, so the hotfix has to be a new version in App Store Connect (for example 2.3.1) with a new build number. If the broken version is still in phased release, pause it immediately and let the hotfix replace it. Because rollback is impossible, feature flags and a hotfix plan must exist before the release, not be invented during the incident.

### "Phased release guarantees only 1% of users get the new version on day one?"

**Common wrong answer:** "Yes, phased release limits exactly how many people get the update." This is a common misunderstanding.

**Better answer:** Phased release only applies to users who have automatic updates turned on: each day Apple picks a randomly selected, growing share of them — 1%, 2%, 5%, 10%, 20%, 50%, 100% over 7 days — and you can pause it (for up to 30 days in total) or release to everyone at any time. Anyone can update manually or download the app fresh from the App Store and get the new version immediately. So phased release slows the spread, but if you need real control over who sees a new feature, you need a server-side feature flag.

### "A build that went through TestFlight doesn't need review for the App Store, right?"

**Common wrong answer:** "Right, it was already reviewed." Or the opposite: "Every TestFlight build has to wait for review."

**Better answer:** Internal testers (members of the team in App Store Connect) get builds without review. External testers require TestFlight App Review, usually for the first build of a version; later builds may not need a full review. Submitting to the App Store is a separate App Review with fuller criteria. Also, TestFlight builds expire after 90 days — a detail interviewers like to ask about when discussing long-running betas.

## Exercise

Your team must ship a payments update before a marketing campaign. Build a release checklist with pre-release checks, rollout strategy, monitoring signals, and stop-ship criteria.
