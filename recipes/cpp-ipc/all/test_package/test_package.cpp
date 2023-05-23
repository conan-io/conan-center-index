#include "libipc/ipc.h"

int main() {
    ipc::channel cc { "my-ipc-channel", ipc::sender | ipc::receiver };

    return EXIT_SUCCESS;
}
