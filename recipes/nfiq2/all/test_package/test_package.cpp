#include <nfiq2_algorithm.hpp>

int main() {
    NFIQ2::Algorithm nfiq2;
    if (!nfiq2.isInitialized() || !nfiq2.isEmbedded()) {
        return 1;
    }
    return 0;
}
