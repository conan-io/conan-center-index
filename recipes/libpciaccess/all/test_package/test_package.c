#include <stdio.h>
#include <pciaccess.h>

int main()
{
    int res = pci_system_init();
    pci_system_cleanup();
    return res;
}
