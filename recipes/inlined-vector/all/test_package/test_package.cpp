#include <inlined_vector.hpp>
#include <iostream>
#include <string>

int main() {
    // Test basic operations with trivial type
    lloyal::InlinedVector<int, 4> numbers;
    numbers.push_back(1);
    numbers.push_back(2);
    numbers.push_back(3);

    if (numbers.size() != 3) {
        std::cerr << "Error: size() returned " << numbers.size() << ", expected 3\n";
        return 1;
    }

    if (numbers[0] != 1 || numbers[1] != 2 || numbers[2] != 3) {
        std::cerr << "Error: element access failed\n";
        return 1;
    }

    // Test with non-trivial type
    lloyal::InlinedVector<std::string, 2> strings;
    strings.emplace_back("hello");
    strings.emplace_back("world");

    if (strings.size() != 2) {
        std::cerr << "Error: string vector size() returned " << strings.size() << ", expected 2\n";
        return 1;
    }

    // Test const member support (compile-time check)
    struct Token {
        const int id;
        std::string text;
        Token(int i, std::string t) : id(i), text(std::move(t)) {}
    };

    lloyal::InlinedVector<Token, 2> tokens;
    tokens.emplace_back(1, "identifier");
    tokens.emplace_back(2, "operator");

    if (tokens.size() != 2 || tokens[0].id != 1) {
        std::cerr << "Error: const member support failed\n";
        return 1;
    }

    std::cout << "inlined-vector test passed successfully!\n";
    return 0;
}
