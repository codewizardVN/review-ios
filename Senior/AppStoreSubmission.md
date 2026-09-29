[English](./AppStoreSubmission.md) | [Tiếng Việt](./AppStoreSubmission.vi.md)

[← Senior-Level Topics](./README.md)

# App Store Submission and Review

## Key Idea

App Review rejections are rarely about a clever edge case — they're almost always a small, well-documented, predictable set of issues. A senior engineer's job is to make sure the app never reaches review with one of them still present.

## What To Review

- Privacy manifest (`PrivacyInfo.xcprivacy`) — a plist in the bundle that declares the data types the app collects, the domains used for tracking, and use of "required reason" APIs (5 categories: file timestamp, system boot time, disk space, active keyboard, `UserDefaults`) with a reason code Apple accepts. Since May 1, 2024 Apple enforces the required-reason part: a build that uses these APIs without declarations is refused by App Store Connect at upload processing (ITMS-91053 error email), before it reaches a reviewer — not just a manual review flag
- App Privacy "nutrition label" in App Store Connect — must match what the app *actually* does, not what it did at last submission; a new analytics SDK or ad network changes this and is a common source of drift
- Common rejection categories — guideline 2.1 (App Completeness: crashes on launch, broken core flow on the reviewer's test account, placeholder content, a required login with no demo account provided), 2.3 (inaccurate or incomplete metadata), 3.1.1 (unlocking digital content/features without In-App Purchase), 4.3 (spam/template apps), 5.1.1 (collecting data or requesting permissions without a clear purpose, or collecting more than needed)
- Demo/test account requirements — App Review needs working credentials for any gated flow; an expired or 2FA-protected demo account is a top cause of "unable to test" rejections
- Metadata rules — screenshots must reflect the actual running app, no names or icons of other platforms/competitors, no placeholder "Lorem ipsum" text, and no stuffing keywords or other brands' names into the name/subtitle
- Encryption export compliance (`ITSAppUsesNonExemptEncryption` in Info.plist) — an app that only uses the OS's built-in encryption (HTTPS/TLS via `URLSession`, Keychain…) usually qualifies as exempt and sets `NO`. If the key is missing, App Store Connect asks the export compliance question for every build and the build sits in "Missing Compliance", unusable for TestFlight or submission until answered. Declaring it wrong (claiming exempt while using custom/non-exempt encryption) is an export-law legal risk, not just a review issue
- Phased release — the App Store releases an update gradually over 7 days (1%, 2%, 5%, 10%, 20%, 50%, 100%) to users with automatic updates on; you can pause it (up to 30 days in total) if the crash rate or a metric regresses, or release to everyone at once. Note: users can still manually download the new version during a phased release, and pausing doesn't pull back what's already shipped — to truly stop it you need an in-app kill switch or a fix release
- Responding to rejection — replying to the reviewer in App Store Connect (Resolution Center) vs submitting an appeal to the App Review Board; distinguishing a guideline misunderstanding (worth appealing with evidence) from an actual policy violation (worth just fixing)

## Example

A submission gets rejected under 5.1.1 because the app requests location "always" access but only uses it in foreground. The fix isn't a metadata argument — it's requesting only the permission you need: call `requestWhenInUseAuthorization()` instead of `requestAlwaysAuthorization()` in code, remove the `NSLocationAlwaysAndWhenInUseUsageDescription` key from Info.plist (keeping only `NSLocationWhenInUseUsageDescription` with a specific explanation), and drop the `location` background mode if it isn't actually used. The reason is that reviewers judge actual runtime behavior (what the app asks for and when it uses it), not the stated intent.

## Practice Questions

- Why does a demo account with 2FA enabled almost guarantee a rejection?
- Why is a privacy manifest omission an automated rejection rather than a human judgment call?
- When is it right to appeal a rejection versus just fixing the flagged issue?

## Senior Take

This is one of the few areas where "we'll fix it after ship" isn't available — a rejected build blocks the whole release train, and a botched appeal can add days. A senior engineer treats App Review readiness as a pre-submission checklist owned by the team (privacy manifest audit, demo account validity, screenshot accuracy), not a surprise discovered after upload, and knows which rejections are worth a documented appeal versus a same-day fix and resubmit.

## Practice Question Answers

### Why does a demo account with 2FA enabled almost guarantee a rejection?

Because the reviewer can't receive the verification code sent to your phone or email, so they get stuck at login and reject with "unable to review the app" (usually guideline 2.1 – App Completeness).

Reviewers work asynchronously, in another time zone, on Apple's devices. An OTP sent by SMS to a teammate's number, or to an inbox nobody reads at 3 a.m., may as well not exist. They won't message you and wait for a code; they record that the core flow was unreachable and send the build back. Every such round costs another day or more.

Practical handling:

- Create a dedicated App Review demo account with 2FA off, or configure the backend so that account accepts a fixed code written in App Review Information.
- Verify the account works right before submitting: not expired, not locked by failed logins, and seeded with sample data so the feature is visible.
- If a flow needs special hardware or location, add a demo mode or attach a demo video in the notes.

Trade-off: an account that bypasses 2FA is a potential hole. Limit its permissions (fake data only, no admin access), monitor its logins, and rotate the password after each release.

### Why is a privacy manifest omission an automated rejection rather than a human judgment call?

Because required-reason API usage is machine-detectable: when you upload a build, Apple scans the binary for those APIs' symbols and compares them with `PrivacyInfo.xcprivacy`, with no human needed.

Since May 1, 2024, App Store Connect refuses new apps and updates that use required-reason APIs without an approved reason (error ITMS-91053 "Missing API declaration"). The API categories are: file timestamp, system boot time, disk space, active keyboard, and `UserDefaults`. The check is a simple match: does the binary reference `UserDefaults`, and does the manifest have an `NSPrivacyAccessedAPICategoryUserDefaults` entry with a valid reason code (e.g. `CA92.1`)? It's yes or no, with no interpretation, so it's automated at build processing — you get an error email before the build ever reaches a reviewer.

On top of that, third-party SDKs on Apple's "commonly used SDKs" list (e.g. Firebase, Alamofire, SDWebImage) must ship their own privacy manifest, and when embedded as a binary (XCFramework) they must also carry the SDK developer's signature; if missing, App Store Connect can block the upload the same way. The fix is usually just upgrading to an SDK version that includes the manifest.

The distinction to make: the data-collection declarations (`NSPrivacyCollectedDataTypes`) and tracking domains are much harder for a machine to verify, so their accuracy still rests mostly on you and on review. A manifest that "passes upload" doesn't mean the app's privacy story is correct.

### When is it right to appeal a rejection versus just fixing the flagged issue?

Appeal when you have evidence the reviewer misunderstood the app or applied the wrong guideline; if the app genuinely violates it, fixing and resubmitting is much faster.

Always start by reading the cited guideline carefully and reproducing exactly what the reviewer saw. There are three situations:

- The reviewer lacked information (couldn't find the feature, didn't understand why a permission is needed): reply in App Store Connect with a clear explanation plus screenshots or video; usually no appeal needed.
- The reviewer applied the wrong guideline (e.g. treating physical goods as digital content that must use IAP): submit an appeal to the App Review Board, arguing from the guideline's exact wording with evidence.
- A real violation (no account deletion, requesting an unused permission): fix it and resubmit the same day.

An often-forgotten point: since 2020, Apple has said bug-fix updates for apps already on the store won't be held back over guideline violations, except for legal issues; you can ask to ship the fix first and resolve the violation in the next submission.

Trade-off: an appeal can take days and isn't guaranteed to succeed. If the release is urgent and the fix is cheap, fix first and argue later.

## Interview Traps

### "We have a privacy manifest, so the nutrition label updates automatically, right?"

**Common wrong answer:** Right, App Store Connect reads `PrivacyInfo.xcprivacy` and fills in the App Privacy label for us.

**Better answer:** They are separate. The manifest lives in the bundle and describes the binary; the nutrition label is still filled in manually in App Store Connect. Xcode can generate a Privacy Report aggregating the app's and SDKs' manifests as a reference for filling the label, but if the two disagree, fixing that is the team's job. Every new SDK means reviewing both.

### "The app collects no data, so does it need a privacy manifest?"

**Common wrong answer:** No, privacy manifests are only for apps with tracking or analytics.

**Better answer:** Required-reason APIs have nothing to do with data collection. Almost every app uses `UserDefaults`, and many read file timestamps or disk space, so they all need declared reasons. Third-party SDKs can also use these APIs even if your own code doesn't. The safe approach is a manifest in the app target, plus checking that each SDK ships its own.

### "The app supports account sign-up; can users just email support to delete their account?"

**Common wrong answer:** Yes, as long as there's some way to request deletion, like an email or a web form.

**Better answer:** Under guideline 5.1.1(v), apps that support account creation must let users initiate account deletion from within the app. Merely deactivating the account or requiring an email isn't enough; highly regulated apps may route through an extra verification process, but the starting point must be in the app. If you use Sign in with Apple, revoke the tokens via Apple's REST API when deleting the account.

## Exercise

Your team is submitting a version that adds a new third-party analytics SDK and a "premium" tier gated behind a paywall with no free trial. List every App Store Connect and code-level item you'd verify before submitting (privacy manifest, nutrition label, demo account, guideline risk areas) and describe the two most likely rejection reasons for this specific change, with the fix for each.
