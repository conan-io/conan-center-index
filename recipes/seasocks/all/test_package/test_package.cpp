#include "seasocks/Server.h"
#include "seasocks/Connection.h"
#include "seasocks/PrintfLogger.h"

#include <thread>
#include <unistd.h>

using namespace seasocks;

// This is a conan test program to ensure the packaging works.
// It's not meant as an example of how best to use Seasocks.
int main(int argc, const char* argv[]) {
    auto logger = std::make_shared<PrintfLogger>();
    Server server(logger);
    server.startListening(0);
    std::thread seasocksThread([&] {
        server.loop();
    });

    sleep(1);

    server.terminate();
    seasocksThread.join();
}
