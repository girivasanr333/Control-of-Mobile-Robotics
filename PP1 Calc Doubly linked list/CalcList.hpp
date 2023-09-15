#ifndef CALCLIST_H
#define CALCLIST_H

#include "CalcListInterface.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>

// Define the Node for the doubly-linked list
class Node {
public:
    double prevTotal;            // Previous total before operation
    FUNCTIONS operation;        // Operation enum (e.g., ADDITION, SUBTRACTION, etc.)
    double operand;             // Operand used for the operation
    Node* next;                 // Pointer to the next node
    Node* prev;                 // Pointer to the previous node

    Node(double pT, FUNCTIONS op, double opd) 
        : prevTotal(pT), operation(op), operand(opd), next(nullptr), prev(nullptr) {}
};

// CalcList class definition that inherits from CalcListInterface
class CalcList : public CalcListInterface {
private:
    Node* head;                 // Head of the linked list
    Node* tail;                 // Tail of the linked list
    double currentTotal;        // Running total of operations
    unsigned int size;          // Number of operations

public:
    CalcList();                 // Constructor
    ~CalcList();                // Destructor
    
    double total() const override;                        // Returns the current total
    void newOperation(const FUNCTIONS func, const double operand) override; // Adds a new operation
    void removeLastOperation() override;                  // Removes the last operation
    std::string toString(unsigned short precision) const override; // Returns string representation
};

#endif /* CALCLIST_H */
