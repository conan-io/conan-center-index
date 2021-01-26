#include <keychain/keychain.h>

using namespace keychain;

int main()
{
    Error error;
    getPassword("conan-test-pkg", "conan-test-srv", "conan-test-user", error);
    return error.type == ErrorType::NotFound ? 0 : 1;
}
