#include <Tpm2.h>

using namespace std;
using namespace TpmCpp;

int main() {
    TpmTbsDevice device;
    Tpm2 tpm(device);

    return 0;
}
