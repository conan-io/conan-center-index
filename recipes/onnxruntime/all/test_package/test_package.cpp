
#include <onnxruntime_cxx_api.h>
#include <iostream>

#ifdef WITH_CUDA
#include <onnxruntime_c_api.h>
#endif

int main() {
  const auto& api = Ort::GetApi();
  std::cout << "Version: " << OrtGetApiBase()->GetVersionString() << std::endl;
  std::cout << "Providers: " << std::endl;
  for(const auto& provider: Ort::GetAvailableProviders())
    std::cout << provider << ", " << std::endl;
  
#ifdef WITH_CUDA
  Ort::SessionOptions session_options;
  OrtSessionOptionsAppendExecutionProvider_CUDA(session_options, 1);
  std::cout << "with cuda!" << std::endl;
#endif
  
  return 0;
}
