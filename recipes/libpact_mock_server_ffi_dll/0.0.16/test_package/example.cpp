#include "pact_mock_server_ffi.h"

int main(int argc, char *argv[]) {
    int port = pact_mock_server_ffi::create_mock_server("{}", "127.0.0.1:0", false);
    pact_mock_server_ffi::mock_server_matched(port);
    return 0;
}
