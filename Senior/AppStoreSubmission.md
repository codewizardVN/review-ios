[English](./AppStoreSubmission.md) | [Tiếng Việt](./AppStoreSubmission.vi.md)

[← Senior-Level Topics](./README.md)

# App Store Submission and Review

## Key Idea

App Review rejections are rarely about a clever edge case — they're almost always a small, well-documented, predictable set of issues. A senior engineer's job is to make sure the app never reaches review with one of them still present.

## What To Review

- Privacy manifest (`PrivacyInfo.xcprivacy`) — declares data collection categories and "required reason" API usage (e.g., `UserDefaults`, disk space APIs, active keyboard) that Apple started enforcing; missing entries cause automated rejection, not just a manual review flag
- App Privacy "nutrition label" in App Store Connect — must match what the app *actually* does, not what it did at last submission; a new analytics SDK or ad network changes this and is a common source of drift
- Common rejection categories — broken core flow on reviewer's test account, incomplete metadata, placeholder content, crashes on launch, sign-in requiring purchase without a demo account, guideline 4.3 (spam/template apps), guideline 5.1.1 (data collection without disclosed purpose)
- Demo/test account requirements — App Review needs working credentials for any gated flow; an expired or 2FA-protected demo account is a top cause of "unable to test" rejections
- Metadata rules — screenshots must reflect the actual app, no mention of other platforms/competitors, no placeholder "Lorem ipsum" text, keyword stuffing in the name/subtitle
- Encryption export compliance (`ITSAppUsesNonExemptEncryption`) — most apps qualify for the standard exemption (HTTPS/TLS only), but flagging this wrong blocks the submission entirely
- Phased release and staged rollout — releasing to a percentage of users first, with the ability to halt rollout if a metric regresses, before a full release
- Responding to rejection — Resolution Center reply vs App Review Board appeal; distinguishing a guideline misunderstanding (worth appealing with evidence) from an actual policy violation (worth just fixing)

## Example

A submission gets rejected under 5.1.1 because the app requests location "always" access but only uses it in foreground. The fix isn't a metadata argument — it's changing `NSLocationAlwaysAndWhenInUseUsageDescription` down to `NSLocationWhenInUseUsageDescription` and removing the capability that isn't actually used, because the review team tests against actual runtime behavior, not the stated intent.

## Practice Questions

- Why does a demo account with 2FA enabled almost guarantee a rejection?
- Why is a privacy manifest omission an automated rejection rather than a human judgment call?
- When is it right to appeal a rejection versus just fixing the flagged issue?

## Senior Take

This is one of the few areas where "we'll fix it after ship" isn't available — a rejected build blocks the whole release train, and a botched appeal can add days. A senior engineer treats App Review readiness as a pre-submission checklist owned by the team (privacy manifest audit, demo account validity, screenshot accuracy), not a surprise discovered after upload, and knows which rejections are worth a documented appeal versus a same-day fix and resubmit.

## Exercise

Your team is submitting a version that adds a new third-party analytics SDK and a "premium" tier gated behind a paywall with no free trial. List every App Store Connect and code-level item you'd verify before submitting (privacy manifest, nutrition label, demo account, guideline risk areas) and describe the two most likely rejection reasons for this specific change, with the fix for each.
