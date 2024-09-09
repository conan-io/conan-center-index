#include <google/cloud/storage/client.h>
#include <iostream>

int main(int argc, char* argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: storage\n";
    return 1;
  }

  // Create aliases to make the code easier to read.
  namespace gcs = google::cloud::storage;

  // Create a client to communicate with Google Cloud Storage. This client
  // uses the default configuration for authentication and project id.
  std::cout << "Testing google-cloud-cpp::storage library " << google::cloud::version_string() << "\n";
  auto client = gcs::Client();
  return 0;
}
