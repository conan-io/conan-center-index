#include <keychain/keychain.h>

using namespace keychain;

// Make sure we actually link keychain
// Note: We cannot make a real call to a keychain function in the CI on Linux.
// It would call to libsecret, which would fail because gnome-keyring-daemon is
// not running on the agent. See also the Keychain CI:
// https://github.com/hrantzsch/keychain/blob/6a4db6048559516fb2f30ad449152a0a3c7138a0/.github/workflows/ci.yml#L49:L53
void never_called(Error &error) {
  getPassword("conan-test-pkg", "conan-test-srv", "conan-test-user", error);
}

int main() {
  Error error;
  return error.type == ErrorType::NoError ? 0 : 1;
}
