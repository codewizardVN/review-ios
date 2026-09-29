import Foundation

// MARK: - Exercise: BankAccount as struct vs class
// Reference: Swift/ValueTypes.md — implement both, then observe transfer(to:amount:) behavior.

// MARK: 1. Struct version

struct BankAccountStruct {
    let id: String
    let owner: String
    var balance: Double

    mutating func transfer(to other: inout BankAccountStruct, amount: Double) {
        self.balance -= amount
        other.balance += amount
    }
}

// MARK: 2. Class version

final class BankAccountClass {
    let id: String
    let owner: String
    var balance: Double

    init(id: String, owner: String, balance: Double) {
        self.id = id
        self.owner = owner
        self.balance = balance
    }

    func transfer(to other: BankAccountClass, amount: Double) {
        // TODO: subtract from self.balance, add to other.balance
        self.balance -= amount
        print("self: \(self.description)")
        other.balance += amount
        print("other: \(other.description)")
    }
    
    var description: String {
        return "BankAccountClass(id: \(id), owner: \(owner), balance: \(balance))"
    }
}

// MARK: 3. Observe: copy a struct account vs assign a class account, then call transfer
var accountA = BankAccountStruct(id: "1", owner: "A", balance: 100)
var accountACopy = accountA

accountACopy.transfer(to: &accountA, amount: 50)
//print("Struct Account A balance: \(accountA.balance)") // Expect 150
//print("Struct Account A Copy balance: \(accountACopy.balance)") // Expect 50

let classA = BankAccountClass(id: "2", owner: "A", balance: 100)
let classAAlias = classA

classAAlias.transfer(to: classA, amount: 50)
//print("Class Account A: \(classA.description)") // Expect 50
//print("Class Account A Alias: \(classAAlias.description)") // Expect 50

// MARK: 4. Write your 3-sentence conclusion here as a comment
// Struct create a clone when assigned -> safe when mutating
// Class create a reference when assigned -> mutating one affects the other
// Use a class for BankAccount can easily lead to unintended side effects if multiple references exist, while struct ensures value semantics and isolation.
