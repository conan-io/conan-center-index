#include <cstdlib>
#include <iostream>

#include "behaviortree_cpp/bt_factory.h"
#include "behaviortree_cpp/basic_types.h"


int main() {
    const auto number = BT::convertFromString<int>("42");
    std::cout << "BehaviorTree.CPP: " << number << std::endl;
    return EXIT_SUCCESS;
}
