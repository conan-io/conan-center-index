
#include <onnxruntime_cxx_api.h>
#include <iostream>

int main() {
  const auto& api = Ort::GetApi();
  std::cout << OrtGetApiBase()->GetVersionString() << std::endl;
  return 0;
}
