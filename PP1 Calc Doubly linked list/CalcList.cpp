#include "CalcList.hpp"

// Constructor
CalcList::CalcList() : head(nullptr), tail(nullptr), currentTotal(0.0), size(0) {}

// Destructor
CalcList::~CalcList() {
    while (head != nullptr) {
        Node* temp = head;
        head = head->next;
        delete temp;
    }
    tail = nullptr;
}

// Return the current total
double CalcList::total() const {
    return currentTotal;
}

// Add a new operation to the list and update the current total
void CalcList::newOperation(const FUNCTIONS func, const double operand) {
    Node* newNode = new Node(currentTotal, func, operand);
    
    if (!head) {
        head = newNode;
        tail = newNode;
    } else {
        tail->next = newNode;
        newNode->prev = tail;
        tail = newNode;
    }
    
    switch (func) {
        case ADDITION:
            currentTotal += operand;
            break;
        case SUBTRACTION:
            currentTotal -= operand;
            break;
        case MULTIPLICATION:
            currentTotal *= operand;
            break;
        case DIVISION:
            if (operand == 0) {
                throw std::runtime_error("Cannot divide by zero!");
            }
            currentTotal /= operand;
            break;
    }
    size++;
}

// Remove the last operation from the list
void CalcList::removeLastOperation() {
    if (!tail) {
        throw std::runtime_error("No operations to remove!");
    }
    
    currentTotal = tail->prevTotal;
    
    if (tail->prev) {
        tail = tail->prev;
        delete tail->next;
        tail->next = nullptr;
    } else {
        delete tail;
        head = nullptr;
        tail = nullptr;
    }
    size--;
}

// Return the string representation of the operations with the given precision
std::string CalcList::toString(unsigned short precision) const {
    std::stringstream ss;
    ss << std::fixed << std::setprecision(precision);
    
    Node* temp = tail;
    int step = size;
    
    while (temp != nullptr) {
        ss << step << ": " << temp->prevTotal;
        
        switch (temp->operation) {
            case ADDITION:
                ss << "+" << temp->operand;
                break;
            case SUBTRACTION:
                ss << "-" << temp->operand;
                break;
            case MULTIPLICATION:
                ss << "*" << temp->operand;
                break;
            case DIVISION:
                ss << "/" << temp->operand;
                break;
        }
        
        double result;
        switch (temp->operation) {
            case ADDITION:
                result = temp->prevTotal + temp->operand;
                break;
            case SUBTRACTION:
                result = temp->prevTotal - temp->operand;
                break;
            case MULTIPLICATION:
                result = temp->prevTotal * temp->operand;
                break;
            case DIVISION:
                result = temp->prevTotal / temp->operand;
                break;
        }
        
        ss << "=" << result << "\n";
        temp = temp->prev;
        step--;
    }
    
    return ss.str();
}
