#include <ipfs_client/logger.h>
#include <iostream>
int main(void) {
    std::cout << ipfs::log::IsInitialized();
    return 0;
}

}
