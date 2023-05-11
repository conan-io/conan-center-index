#include <google/cloud/spanner/client.h>
#include <iostream>

int main(int argc, char *argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: spanner\n";
    return 1;
  }
  auto const project_id =  std::string{"test-only-invalid"};
  auto const instance_id = std::string{"test-only-invalid"};
  auto const database_id =    std::string{"test-only-invalid"};
  std::cout << "Testing google-cloud-cpp::spanner library " << google::cloud::version_string() << "\n";
  namespace spanner = ::google::cloud::spanner;
  auto client = spanner::Client(
      spanner::MakeConnection(spanner::Database(project_id, instance_id, database_id)));
  return 0;
}
