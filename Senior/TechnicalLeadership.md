[English](./TechnicalLeadership.md) | [Tiếng Việt](./TechnicalLeadership.vi.md)

[← Senior Topics](./README.md)

# Technical Leadership

## What It Looks Like

- Setting technical direction and making it visible to the team
- Raising risks early — not just executing tasks
- Unblocking others rather than just doing it yourself
- Mentoring through questions, not just answers
- Writing RFCs or design docs when decisions have long-term impact

## Mentoring Junior and Mid-Level Engineers

- Ask what they have tried before giving the answer
- Review their PRs with explanation, not just approval/rejection
- Pair program on hard problems so they learn the process
- Let them lead small features with your support

## Technical Decisions Under Pressure

- State trade-offs explicitly — "we can ship faster with X but will pay Y later"
- Document the decision and why — decision log helps future engineers
- Avoid solutioning before understanding — ask clarifying questions first

## Practice Questions

- If the team wants to ship quickly but code quality is poor, what do you do?
- If there is architectural disagreement, how do you handle it?
- How do you balance technical debt and product delivery?

## Senior Take

Technical leadership is not about being the best programmer on the team. It is about raising the capability of the whole team, making good decisions under uncertainty, and communicating clearly with both engineers and stakeholders.

## Practice Question Answers

### If the team wants to ship quickly but code quality is poor, what do you do?

I don't pick a side between speed and quality; I make clear what concrete damage the poor quality is causing, then add the cheapest guardrails so the team keeps shipping fast without piling up risk.

Answer structure (situation → action → result):

- **Situation:** the team ships every week, but every release comes with 2–3 hotfixes and the crash-free rate is falling.
- **Action:**
  1. Gather data — hotfix count, recurring bugs, rework time — to talk in numbers instead of a vague "the code is bad".
  2. Add cheap, automated guardrails: SwiftLint on CI, mandatory unit tests for money and login logic, a PR template with a short checklist.
  3. Agree with the team on a minimal "definition of done".
  4. Talk to the PM in terms of cost: how many team-days each hotfix consumes.
  5. Lead by example — small PRs, with tests, reviewed quickly — so the new process doesn't slow anyone down.
- **Result:** after a few sprints hotfixes go down, and speed doesn't drop because there is less rework.

The key is not to blame individuals; poor quality usually comes from deadline pressure or missing process, not from lazy people.

Trade-off: sometimes shipping fast with imperfect code is the right call — prototypes, A/B experiments, features that may be dropped. In that case, write down the debt and the cleanup plan instead of banning it outright.

### If there is architectural disagreement, how do you handle it?

I move the disagreement from "whose opinion" to "which criteria matter to us", then make a time-boxed decision and write it down.

Structure:

1. **Understand each option:** ask each side to present the problem they want to solve, not only their solution. Many disagreements are really two sides optimizing for different goals.
2. **Agree on criteria first:** testability, onboarding time, build time, migration risk, deadline.
3. **Compare with evidence:** a short RFC, or a 1–2 day spike on a real screen.
4. **Decide:** if there's no consensus, the accountable person (tech lead or owner) decides, following "disagree and commit". Record it in an ADR (architecture decision record) with the reasoning and the conditions for revisiting it.
5. **Follow up:** after a while, check whether the decision achieved its goals.

Example with the SwiftUI vs UIKit situation in the exercise, with a 6-week deadline: I might propose keeping UIKit for flows already in progress, using SwiftUI for new screens via `UIHostingController`, and revisiting after the release. Both sides see their concerns taken into account.

Trade-off: not every decision needs an RFC. Decide quickly on things that are easy to reverse; invest process only in decisions that are hard to reverse.

### How do you balance technical debt and product delivery?

I treat technical debt as something managed continuously, not a big project that needs separate approval: prioritize debt by its impact on delivery, and tie paying it down to product work.

How:

- **Keep a debt list with impact:** for example "Checkout module has no tests, every change costs 2 extra days of QA", "the build takes 12 minutes, each engineer loses a few hours a week". Debt with no measurable impact gets low priority.
- **Pay down debt where features are coming:** when building a feature in Checkout, add time to write tests and extract logic.
- **A fixed budget:** for example 15–20% of each sprint's capacity, agreed with the PM up front, instead of asking every time.
- **High-risk debt is handled like a bug:** security, crashes, SDKs about to lose support, new mandatory App Store requirements such as the privacy manifest.
- **Report results in product language:** fewer hotfixes, faster feature delivery.

Example to tell in an interview: "I proposed spending part of two sprints adding tests and pulling networking out of the Checkout view controllers; afterwards features in that area shipped noticeably faster with fewer bugs." Use real numbers from your own experience.

Trade-off: while a product is still searching for product-market fit, accept more debt; a mature product with many users needs a bigger paydown budget.

## Interview Traps

### "Tell me about a time you disagreed with your team or manager"

**Common wrong answer:** Telling a story where you were completely right and the others were wrong, or saying "I've never really disagreed with anyone". Both signal a lack of self-awareness or dodging the question.

**Better answer:** Pick a real story, tell it as situation → action → result, and emphasize that you listened, used data, and kept the relationship healthy. A story where you didn't win but did "disagree and commit" and supported the shared decision is often very convincing. Finish with what you learned.

### "When the team is behind schedule, what do you do?"

**Common wrong answer:** "I take all the hard tasks and work weekends to catch up." It sounds dedicated but is a red flag in a leadership round.

**Better answer:** Hero culture makes you the bottleneck and raises the risk when you're away (bus factor). A senior multiplies the team's capability: removing blockers, cutting scope with the PM, splitting work sensibly, pairing with whoever is stuck, writing docs. Doing the hard part yourself is still right when it's truly urgent, but pair it with knowledge sharing so someone else can do it next time.

### Saying "we" or "I" when describing achievements

**Common wrong answer:** Saying "we did..." from start to finish, so the interviewer can't tell what your role was; or the opposite, "I" everywhere as if you did it all alone.

**Better answer:** Be clear about your part ("I spotted the problem, I wrote the RFC, I convinced the PM to allocate time") and credit the team's contributions. Add measurable results where possible, such as fewer crashes, shorter build times, a faster release cycle. The interviewer is looking for evidence of your individual impact within a team setting.

## Exercise

Your team is split: half want to migrate to SwiftUI now, half want to stay on UIKit. A product deadline is in 6 weeks. Write a one-page decision doc covering: the trade-offs of each option, your recommendation, and how you would communicate it to both the engineering team and the product manager.
