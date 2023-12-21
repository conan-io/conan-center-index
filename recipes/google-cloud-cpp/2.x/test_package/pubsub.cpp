#include <google/cloud/pubsub/publisher.h>
#include <iostream>

int main(int argc, char* argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: pubsub\n";
    return 1;
  }
  auto const project_id = std::string{"test-only-invalid"};
  auto const topic_id = std::string{"test-only-invalid"};
  std::cout << "Testing google-cloud-cpp::pubsub library " << google::cloud::version_string() << "\n";
  namespace pubsub = google::cloud::pubsub;
  auto publisher = pubsub::Publisher(
      pubsub::MakePublisherConnection(pubsub::Topic(project_id, topic_id)));
  return 0;
}
