[English](./Day3_SwiftUI.md) | [Tiếng Việt](./Day3_SwiftUI.vi.md)

# Day 3: SwiftUI

## Goal

Nắm được state flow và lifecycle của SwiftUI.

## Topics

- `View` lifecycle
- `@State`
- `@Binding`
- `@ObservedObject`
- `@StateObject`
- `@EnvironmentObject`
- Dependency injection
- Navigation
- Rendering performance
- UIKit interoperability

## What You Should Be Able To Explain

- Khi nào dùng từng property wrapper
- Vì sao `@StateObject` quan trọng với object ownership
- Data flow một chiều trong SwiftUI
- Cách inject dependency mà không làm mờ ownership
- Các lỗi phổ biến gây re-render không cần thiết
- Khi nào nên bridge với UIKit

## Practice Questions

- Vì sao view bị reload liên tục?
- Khi nào dùng `EnvironmentObject` là hợp lý, khi nào là abuse?
- Một list lớn bị lag thì bạn debug từ đâu?

## Senior Notes

- SwiftUI ở level senior không chỉ là viết UI nhanh.
- Trọng tâm là state ownership, side effects, performance, architecture fit.
