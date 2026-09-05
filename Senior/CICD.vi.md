[English](./CICD.md) | [Tiếng Việt](./CICD.vi.md)

[← Senior Topics](./README.vi.md)

# CI/CD cho Mobile

## Những gì Senior cần nắm

- Pipeline tự động build, test, code-signing (Fastlane + GitHub Actions/GitLab CI/Bitrise)
- Chiến lược code signing — manual vs certificate/profile quản lý bằng `match`/fastlane
- Tự động hóa phân phối — TestFlight, Firebase App Distribution, internal beta track
- Build matrix — nhiều scheme/configuration (dev/staging/prod), nhiều target
- Quản lý secrets — API key, signing certificate, không commit vào source control
- Tốc độ pipeline — caching (`DerivedData`, SPM/CocoaPods), chạy song song test target, incremental build

## Luồng điển hình

1. Mở PR → lint (SwiftLint/SwiftFormat) + unit test chạy trên CI
2. Merge vào main → build, chạy full test suite, upload dSYM lên crash reporting
3. Tag/release branch → Fastlane lane build, sign, upload lên TestFlight
4. Promotion thủ công hoặc tự động → submit App Store kèm release note và phased rollout

## Ví dụ (Fastlane lane)

```ruby
lane :beta do
  increment_build_number(xcodeproj: "App.xcodeproj")
  match(type: "appstore", readonly: true)
  build_app(scheme: "App-Production")
  upload_to_testflight(skip_waiting_for_build_processing: true)
  slack(message: "New beta build uploaded to TestFlight ✅")
end
```

## Câu hỏi luyện tập

- Bạn giữ đồng bộ signing credential giữa các thành viên team như thế nào mà không phải gửi file `.p12` qua email?
- Chiến lược của bạn khi CI build fail dù build local pass?
- Bạn sẽ tăng tốc một pipeline CI 40 phút như thế nào mà không cắt giảm test coverage?

## Góc nhìn Senior

Việc sở hữu CI/CD trong thực tế thường là điểm phân biệt senior với mid-level mobile engineer — khả năng debug một pipeline chập chờn, sở hữu setup signing (`match` + repo certificate dùng chung), và thiết kế build matrix không biến thành 20 phút build dư thừa mỗi PR. Tín hiệu phỏng vấn không phải "bạn đã dùng Fastlane chưa" — mà là bạn có suy luận được các failure mode: provisioning profile hết hạn âm thầm, cache làm hỏng một build, race giữa hai lane cùng ghi vào một keychain.

## Bài tập

Thiết kế một pipeline CI/CD cho team có 3 build flavor (dev, staging, production), chạy trên GitHub Actions với Fastlane. Nêu rõ: điều gì trigger mỗi lane, signing certificate được chia sẻ thế nào giữa máy của 5 kỹ sư và CI mà không commit vào repo, và điều gì xảy ra tự động khi một test run fail so với khi bước code-signing fail.
