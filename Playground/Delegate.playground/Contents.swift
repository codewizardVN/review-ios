import Foundation
import UIKit

// 1. Define a protocol for handling payment results
@MainActor
protocol PaymentDelegate: AnyObject {
    func paymentDidSucceed(transactionID: String)
    func paymentDidFail(error: Error)
}

// 2. Class to handle payment processing
@MainActor
class PaymentProcessor {
    weak var delegate: PaymentDelegate?

    func processPayment(amount: Double) {
        Task {
            do {
                let txID = try await callPaymentAPI(amount: amount)
                delegate?.paymentDidSucceed(transactionID: txID)
            } catch {
                delegate?.paymentDidFail(error: error)
            }
        }
    }

    private func callPaymentAPI(amount: Double) async throws -> String {
        // This is a mock implementation. In a real scenario, you would make a network call here.
        try await Task.sleep(nanoseconds: 1_000_000_000)
        return "TX1234567890"
    }
}

@MainActor
class CheckoutViewController: UIViewController, PaymentDelegate {
    let paymentProcessor = PaymentProcessor()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        paymentProcessor.delegate = self
        paymentProcessor.processPayment(amount: 49.99)
    }
    
    func paymentDidSucceed(transactionID: String) {
        print("Payment succeeded with transaction ID: \(transactionID)")
        // Update UI or navigate to success screen
    }
    
    func paymentDidFail(error: Error) {
        print("Payment failed with error: \(error.localizedDescription)")
        // Update UI or show error message
    }
}



