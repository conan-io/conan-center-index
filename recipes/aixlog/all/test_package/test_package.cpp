#include <aixlog.hpp>
#include <cstdlib>

int main() {
    AixLog::Log::init<AixLog::SinkCout>(AixLog::Severity::trace);
    LOG(INFO) << "conan\n";
    return EXIT_SUCCESS;
}
