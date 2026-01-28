#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#include <casbin/casbin.h>

int main() {
    std::vector<std::string> a = {"alice", "bob"};
    std::vector<std::string> b = {"alice", "bob"};
    
    if (casbin::ArrayEquals(a, b) && casbin::Join(a, ",") == "alice,bob") {
        std::cout << "casbin test ok" << std::endl;
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}
