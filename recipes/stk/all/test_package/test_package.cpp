#include <stk/Stk.h>
#include <iostream>

int main() {
    stk::Stk::setSampleRate(44100.0);
    std::cout << "STK sample rate set to: " << stk::Stk::sampleRate() << "\n";
    return 0;
}