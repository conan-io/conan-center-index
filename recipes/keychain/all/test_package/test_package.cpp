#include <keychain/keychain.h>

using namespace keychain;

int main()
{
    Error error;
    return error.type == ErrorType::NoError ? 0 : 1;
}
