#include <google/cloud/bigtable/table.h>

int main(int argc, char *argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: bigtable\n";
    return 1;
  }
  auto const project_id =  std::string{"test-only-invalid"};
  auto const instance_id = std::string{"test-only-invalid"};
  auto const table_id =    std::string{"test-only-invalid"};
  std::cout << "Testing google-cloud-cpp::bigtable library " << google::cloud::version_string() << "\n";
  namespace cbt = ::google::cloud::bigtable;
  auto table = cbt::Table(
      cbt::MakeDataConnection(), cbt::TableResource(project_id, instance_id, table_id));
  return 0;
}
