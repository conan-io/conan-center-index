#include <cstdlib>
#include <iostream>

#define LLM_JSON_IMPLEMENTATION
#include <llm/llm.hpp>

int main() {
    auto value = llm::json::parse("{\"model\": \"test\", \"tokens\": 42}");
    std::cout << "llm-cpp " << LLM_CPP_VERSION << ": " << value.dump() << std::endl;
    return EXIT_SUCCESS;
}
