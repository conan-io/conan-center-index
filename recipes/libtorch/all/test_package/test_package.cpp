#include <torch/torch.h>
#include <iostream>

int main() {
  const torch::Tensor tensor1 = torch::rand({3, 2});
  std::cout << tensor1 << std::endl;
  const torch::Tensor tensor2 = torch::eye(3);
  std::cout << tensor2 << std::endl;
}
