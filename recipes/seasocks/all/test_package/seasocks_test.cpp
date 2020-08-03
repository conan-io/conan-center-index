#include "seasocks/Server.h"
#include "seasocks/Connection.h"
#include "seasocks/IgnoringLogger.h"

#include <thread>
#include <unistd.h>

using namespace seasocks;


int main(int argc, const char *argv[]) {
    auto logger = std::make_shared<IgnoringLogger>();
    Server server(logger);
    server.startListening(0);
    std::thread seasocksThread([&]{
        server.loop();
    });

    sleep(1);

    server.terminate();
    seasocksThread.join();
}
