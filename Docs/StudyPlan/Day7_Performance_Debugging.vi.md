[English](./Day7_Performance_Debugging.md) | [Tiếng Việt](./Day7_Performance_Debugging.vi.md)

# Day 7: Performance and Debugging

## Goal

Ôn các vấn đề thường gặp khi app thật chạy chậm, tốn bộ nhớ, hoặc crash.

## Topics

- Main thread discipline
- Memory leaks
- Retain cycle detection
- Instruments
- Memory Graph
- Startup time
- Rendering issues
- Large-list optimization

## What You Should Be Able To Explain

- Cách tiếp cận khi app bị lag
- Cách tìm leak và retain cycle
- Vì sao UI bị drop frame
- Startup time bị ảnh hưởng bởi đâu
- Khi nào optimize là cần thiết, khi nào là premature

## Practice Questions

- Một màn hình scroll lag, bạn sẽ kiểm tra gì trước?
- Crash ngẫu nhiên ngoài production, bạn tiếp cận thế nào?
- Tại sao image loading có thể làm app giật?

## Senior Notes

- Hãy trả lời theo quy trình: observe, isolate, measure, fix, verify.
