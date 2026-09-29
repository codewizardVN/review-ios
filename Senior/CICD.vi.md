[English](./CICD.md) | [Tiếng Việt](./CICD.vi.md)

[← Chủ đề Senior](./README.vi.md)

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
  setup_ci if ENV["CI"]   # tạo keychain tạm trên CI để match cài certificate, tránh lỗi keychain bị khóa
  app_store_connect_api_key(
    key_id: ENV["ASC_KEY_ID"],
    issuer_id: ENV["ASC_ISSUER_ID"],
    key_content: ENV["ASC_KEY_P8"]   # nội dung file .p8, lấy từ secret của CI
  )
  # build number phải lớn hơn build đã upload; lấy từ TestFlight để CI không cần commit lại số build
  increment_build_number(
    xcodeproj: "App.xcodeproj",
    build_number: latest_testflight_build_number + 1
  )
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

## Đáp án câu hỏi luyện tập

### Bạn giữ đồng bộ signing credential giữa các thành viên team như thế nào mà không phải gửi file `.p12` qua email?

Tôi dùng một nguồn chung, được mã hóa và có phân quyền rõ ràng — phổ biến nhất là fastlane `match`, hoặc cloud-managed signing của Xcode và Xcode Cloud.

Với `match`:

- Certificate và provisioning profile được lưu mã hóa trong một private Git repo riêng (hoặc S3, Google Cloud Storage), khóa bằng passphrase `MATCH_PASSWORD`.
- Một người có quyền admin tạo certificate một lần; các engineer khác và CI chạy `match(type: "development", readonly: true)` để tải về và cài vào keychain.
- CI luôn dùng `readonly: true` như lane `beta` ở ví dụ trên, để không vô tình tạo mới hay revoke certificate.
- Passphrase và App Store Connect API key (file `.p8`) nằm trong secret của CI (GitHub Actions secrets), không nằm trong repo.

Lựa chọn khác: automatic signing với cloud-managed certificate — Xcode lấy distribution certificate qua tài khoản hoặc App Store Connect API key khi archive và export, còn Xcode Cloud tự quản lý signing hoàn toàn. Cách này phù hợp team nhỏ, ít thứ phải tự vận hành.

Trên CI nên dùng App Store Connect API key thay cho Apple ID với mật khẩu, vì không vướng 2FA và có thể revoke riêng từng key.

Trade-off: `match` tập trung hóa mọi thứ, nên nếu ai đó chạy `match nuke` hoặc passphrase bị lộ thì cả team bị ảnh hưởng. Cần giới hạn quyền ghi vào repo certificate cho 1–2 người, và đổi passphrase khi có người rời team.

### Chiến lược của bạn khi CI build fail dù build local pass?

Tôi coi đây là khác biệt về môi trường cho đến khi chứng minh được điều ngược lại, và tìm khác biệt đó một cách có hệ thống thay vì bấm re-run.

Các bước:

1. **Đọc log để biết fail ở bước nào:** resolve package, compile, sign, hay test. Lưu `.xcresult` bundle từ CI làm artifact để xem chi tiết.
2. **So sánh môi trường:** version Xcode (runner image có thể đổi Xcode mặc định), simulator runtime, version Ruby và fastlane, `Package.resolved` đã được commit chưa.
3. **Kiểm tra trạng thái sạch:** máy local thường có DerivedData cũ, file chưa commit, hoặc scheme chưa được đánh dấu shared. Clone mới, xóa DerivedData, rồi chạy đúng lệnh mà CI chạy.
4. **Nếu là test:** CI thường chậm hơn, chạy song song và theo thứ tự khác, nên dễ lộ race condition, test phụ thuộc lẫn nhau, timeout quá ngắn, hoặc phụ thuộc timezone và locale của máy.
5. **Nếu là signing:** profile hết hạn, keychain trên CI bị khóa, thiếu secret.

Sau khi tìm ra thì sửa tận gốc: ghim version Xcode, commit `Package.resolved`, làm test deterministic.

Trade-off: tự động retry flaky test giúp pipeline xanh nhưng che giấu vấn đề. Nếu dùng retry, hãy đánh dấu và theo dõi các test flaky để sửa, đừng để retry trở thành thói quen.

### Bạn sẽ tăng tốc một pipeline CI 40 phút như thế nào mà không cắt giảm test coverage?

Tôi đo trước rồi tối ưu phần tốn nhất; thường thời gian nằm ở resolve dependency, build lại từ đầu nhiều lần, và chạy test tuần tự.

Các cách:

- **Đo:** thời gian từng step trong pipeline, và `xcodebuild -showBuildTimingSummary` để biết compile, link hay build script tốn thời gian.
- **Build một lần, test nhiều lần:** `build-for-testing` một lần, rồi `test-without-building` trên nhiều job hoặc nhiều simulator song song; bật parallel testing trong test plan.
- **Cache có chọn lọc:** cache SPM package (`-clonedSourcePackagesDirPath`) và Ruby gem với key theo `Package.resolved` và `Gemfile.lock`.
- **Chạy đúng thứ ở đúng lúc:** PR chạy unit test và test của module bị ảnh hưởng; UI test đầy đủ chạy khi merge hoặc nightly. Coverage không giảm, chỉ dời thời điểm chạy.
- **Bỏ việc thừa:** không build lại cùng một thứ cho nhiều job, chạy SwiftLint ở job riêng hoặc chỉ trên file thay đổi.
- **Máy mạnh hơn:** chọn runner Apple Silicon có nhiều CPU/RAM hơn (ví dụ runner loại lớn của GitHub Actions hoặc máy Mac mini tự host). Hiện nay runner macOS mặc định của các dịch vụ lớn đã là Apple Silicon; nếu team vẫn dùng runner Intel cũ thì chuyển sang Apple Silicon thường nhanh hơn rõ rệt, và Xcode/macOS mới cũng đang dần bỏ hỗ trợ Intel.

Trade-off: dời UI test sang nightly nghĩa là lỗi được phát hiện muộn hơn vài giờ, nên cần quy tắc rõ ai sửa khi nightly đỏ. Cache cũng làm pipeline phức tạp hơn — khi build có lỗi lạ, bước đầu tiên là chạy lại không có cache.

## Bẫy phỏng vấn

### "CI báo lỗi signing. Bạn làm gì?"

**Dễ trả lời sai:** "Chạy `match nuke` rồi tạo lại hết certificate cho sạch." Lệnh này revoke certificate, làm mọi profile dùng certificate đó mất hiệu lực với cả team và CI.

**Nên trả lời:** Đọc lỗi cụ thể trước: profile hết hạn, thiếu device trong development profile, thiếu entitlement mới (ví dụ vừa bật Push hoặc App Groups), hay keychain trên CI chưa được unlock. Phần lớn chỉ cần người có quyền chạy `match` không ở chế độ readonly để làm mới profile. Revoke certificate là biện pháp cuối cùng, cần báo cả team, vì các build nội bộ (development, ad hoc) đang dùng nó có thể bị ảnh hưởng. App đã phát hành trên App Store thì không bị ảnh hưởng, vì Apple ký lại app khi phân phối qua App Store; việc bị chặn chủ yếu là ký và upload build mới cho tới khi có certificate mới.

### "API key để ở đâu cho an toàn?"

**Dễ trả lời sai:** "Để trong `.xcconfig` hoặc Info.plist, không commit là được." Hoặc tin rằng obfuscate key trong app là đủ bí mật.

**Nên trả lời:** Secret của CI (signing, App Store Connect API key) nằm trong secret store của CI và chỉ được đưa vào lúc chạy. Nhưng bất kỳ key nào được nhúng vào app binary thì đều có thể bị trích ra, dù có obfuscate. Key thật sự nhạy cảm phải nằm ở backend, app gọi qua server của bạn; key bắt buộc ở client thì phải được giới hạn quyền và có thể rotate.

### "Cache toàn bộ DerivedData giữa các lần chạy thì luôn nhanh hơn?"

**Dễ trả lời sai:** "Đúng, cache càng nhiều càng nhanh." Đây chính là nguồn gốc của các build lỗi khó hiểu.

**Nên trả lời:** DerivedData rất lớn, thời gian upload và download cache có thể lớn hơn thời gian tiết kiệm được. Nếu cache key không gắn với version Xcode và lockfile, cache cũ có thể gây build lỗi hoặc build ra kết quả sai (cache poisoning). Cache SPM package và gem an toàn và hiệu quả hơn; nếu cache build output thì key phải chặt, và luôn có cách chạy lại không cache.

## Bài tập

Thiết kế một pipeline CI/CD cho team có 3 build flavor (dev, staging, production), chạy trên GitHub Actions với Fastlane. Nêu rõ: điều gì trigger mỗi lane, signing certificate được chia sẻ thế nào giữa máy của 5 kỹ sư và CI mà không commit vào repo, và điều gì xảy ra tự động khi một test run fail so với khi bước code-signing fail.
