#include <google/cloud/functions/framework.h>
#include <iostream>

int main(int, char*[]) {
  std::cout << google::cloud::functions::VersionString() << "\n";
  return 0;
}
