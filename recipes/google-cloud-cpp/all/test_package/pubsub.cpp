#include "google/cloud/pubsub/publisher.h"
#include <iostream>
#include <stdexcept>

namespace pubsub = ::google::cloud::pubsub;

int main(int argc, char *argv[]) try
{
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <project-id> <topic-id>\n";
        return 1;
    }

    std::string const project_id = argv[1];
    std::string const topic_id = argv[2];

    // Create a namespace alias to make the code easier to read.
    auto publisher = pubsub::Publisher(pubsub::MakePublisherConnection(pubsub::Topic(project_id, topic_id), {}));
    auto id = publisher.Publish(pubsub::MessageBuilder{}.SetData("Hello World!").Build()).get();

    if (!id)
    {
        throw std::runtime_error(id.status().message());
    }
    std::cout << "Hello World published with id=" << *id << "\n";

    return 0;
}
catch (std::exception const &ex)
{
    std::cerr << "Standard exception raised: " << ex.what() << "\n";
    return 0;
}
