#include "llama.h"
#include "build-info.h"
#include "download.h"
#include <iostream>
int main() {
  llama_model_params params = llama_model_default_params();
  auto repo_tag = common_download_split_repo_tag("ggml-org/models:F16");
  std::cout << "Main GPU: " << params.main_gpu << " build: " << llama_build_info() << " tag: " << repo_tag.second << std::endl;

  return 0;
}
