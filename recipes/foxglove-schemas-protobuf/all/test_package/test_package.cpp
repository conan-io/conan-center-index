#include <foxglove/SceneUpdate.pb.h>


int main() {
    foxglove::SceneUpdate msg;
    auto* entity = msg.add_entities();
    return 0;
}
