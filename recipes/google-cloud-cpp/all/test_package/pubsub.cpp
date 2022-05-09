#include "google/cloud/pubsub/publisher.h"
#include <iostream>
#include <stdexcept>

namespace pubsub = ::google::cloud::pubsub;

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <project-id> <topic-id>\n";
        return 1;
    }

    std::string const project_id = argv[1];
    std::string const topic_id = argv[2];

    auto publisher = pubsub::Publisher(pubsub::MakePublisherConnection(pubsub::Topic(project_id, topic_id), {}));
    // FIXME: It needs working credentials
    // auto id = publisher.Publish(pubsub::MessageBuilder{}.SetData("Hello World!").Build()).get();
    // if (!id)
    // {
    //     std::cerr << "Failed to send message\n";
    //     return 0;
    // }
    //std::cout << "Hello World published with id=" << *id << "\n";
    std::cout << "pubsub test done\n";
    return 0;
}
