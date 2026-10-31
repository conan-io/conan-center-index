#include "eckit/runtime/Main.h"
#include "eckit/log/Log.h"

int main(int argc, char** argv) {
    eckit::Main::initialise(argc, argv);
    eckit::Log::info() << "Application started!" << std::endl;
    return 0;
}
