#include <stdlib.h>
#include <pciaccess.h>

int main(void) {
    pci_system_init();
    pci_system_cleanup();
    return EXIT_SUCCESS;
}
