#include "pybind11_json/pybind11_json.hpp"

#include "nlohmann/json.hpp"

#include "pybind11/embed.h"
#include "pybind11/pybind11.h"

#include <iostream>
#include <string>

namespace nl = nlohmann;
namespace py = pybind11;
using namespace pybind11::literals;

int main() {
    // Required to run a standalone C++ application (https://pybind11.readthedocs.io/en/stable/advanced/embedding.html)
    py::scoped_interpreter guard{};

    const py::dict original_py_dict{"number"_a=1234, "hello"_a="world"};
    
    const nl::json converted_nl_json{original_py_dict};
    std::cout << "Converted nlohmann::json contents: " <<  converted_nl_json << std::endl;
    
    const py::dict converted_py_dict = converted_nl_json.front();  // assigning the only list element

    std::cout << "Converted py::dict contents: {hello:" << converted_py_dict["hello"].cast<std::string>()
              << ", number:" << converted_py_dict["number"].cast<int>()  << "}" << std::endl;

    return EXIT_SUCCESS;
}
