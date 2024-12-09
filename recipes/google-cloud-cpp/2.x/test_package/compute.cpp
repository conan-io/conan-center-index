#include <google/cloud/compute/disks/v1/disks_client.h>

int main(int argc, char *argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: compute\n";
    return 1;
  }
  std::cout << "Testing google-cloud-cpp::compute library " << google::cloud::version_string() << "\n";
  namespace disks = ::google::cloud::compute_disks_v1;
  auto client = disks::DisksClient(disks::MakeDisksConnectionRest());
  return 0;
}
