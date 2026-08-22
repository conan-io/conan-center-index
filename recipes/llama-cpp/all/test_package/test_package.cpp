#include "llama.h"
#include <iostream>
int main() {
  llama_model_params params = llama_model_default_params();
  std::cout << "Main GPU: " << params.main_gpu << std::endl;

  return 0;
}
