// Minimal consumer used by `conan create .` to verify the CxxScript package
// installs and links correctly.
#include "CxxScript/ScriptManager.h"

#include <iostream>

using namespace Script;

int main() {
  ScriptManager manager;
  std::vector<CompilationError> errors;

  const std::string source = R"(
    int32 add(int32 a, int32 b) {
      return a + b;
    }
  )";

  if (!manager.loadScriptSource(source, "test_package.script", errors)) {
    for (const auto &error : errors) {
      std::cerr << error.toString() << std::endl;
    }
    return 1;
  }

  Value result;
  std::string errorMessage;
  std::vector<Value> args = {static_cast<int32_t>(2), static_cast<int32_t>(3)};

  if (!manager.executeProcedure("add", args, result, errorMessage)) {
    std::cerr << errorMessage << std::endl;
    return 1;
  }

  std::cout << "add(2, 3) = " << std::get<int32_t>(result) << std::endl;
  return std::get<int32_t>(result) == 5 ? 0 : 1;
}
