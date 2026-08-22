#include <cstdlib>
#include <libvault/VaultClient.h>

int main(void) {
    Vault::Config config = Vault::ConfigBuilder().build();
    return EXIT_SUCCESS;
}
