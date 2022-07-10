#include <vectorclass.h>

#include <iostream>
#include <stdexcept>
#include <string>

void print_instruction_set() {
   // 0          = 80386 instruction set
   // 1 or above = SSE (XMM) supported by CPU (not testing for OS support)
   // 2 or above = SSE2
   // 3 or above = SSE3
   // 4 or above = Supplementary SSE3 (SSSE3)
   // 5 or above = SSE4.1
   // 6 or above = SSE4.2
   // 7 or above = AVX supported by CPU and operating system
   // 8 or above = AVX2
   // 9 or above = AVX512F
   //10 or above = AVX512VL, AVX512BW, AVX512DQ
    const auto instruction_set = instrset_detect();
    switch (instruction_set) {
        case 10:
            std::cout << "AVX512VL, AVX512BW, AVX512DQ\n";
        case 9:
            std::cout << "AVX512F\n";
        case 8:
            std::cout << "AVX2\n";
        case 7:
            std::cout << "AVX supported by CPU and operating system\n";
        case 6:
            std::cout << "SSE4.2\n";
        case 5:
            std::cout << "SSE4.1\n";
        case 4:
            std::cout << "Supplementary SSE3 (SSSE3)\n";
        case 3:
            std::cout << "SSE3\n";
        case 2:
            std::cout << "SSE2\n";
        case 1:
            std::cout << "SSE (XMM) supported by CPU (not testing for OS support)\n";
        case 0:
            std::cout << "80386 instruction set\n";
            break;
        default:
            throw std::runtime_error("Unexpected instruction set " + std::to_string(instruction_set));
   }
}

int main() {
    print_instruction_set();

    Vec4i a(10, 11, 12, 13);
    Vec4i b(20, 21, 22, 23);

    Vec4i c = a + b;
    for (int i = 0; i < c.size(); ++i) {
        std::cout << " " << c[i];
    }
    std::cout << std::endl;

    return 0;
}
