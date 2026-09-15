// Proves the package is consumable, without needing a broker.
//
// parseLevel, levelName and hexDump are declared in motus/Logger.hpp and defined in the
// compiled Logger translation unit, so linking this exercises the static library rather
// than just the headers. versionString() comes from motus/Version.hpp, which CMake
// generates at build time -- including it here checks that the generated header was
// installed alongside the hand-written ones.
//
// The guarded include of motus/AmqpConnection.hpp tests the packaging rather than the
// library. That header is installed and reaches <amqpcpp.h> and <boost/asio/*.hpp>, so it
// compiles only if both requirements carry transitive_headers=True; on Windows it also
// needs the _WIN32_WINNT define that package_info() restates, because package() removes the
// exported CMake config that upstream put it on. The guard reads
// motus/transport/Config.hpp, the generated header recording which backends this build
// contains, so the test follows the recipe's options without having to know them.
//
// Nothing below emits a log record, so the logger's sink thread never starts and the test
// stays deterministic on every platform ConanCenter builds.

#include <iostream>

#include <motus/Logger.hpp>
#include <motus/Version.hpp>
#include <motus/transport/Config.hpp>

#ifdef MOTUS_WITH_AMQPCPP
#include <motus/AmqpConnection.hpp>
#endif

int main()
{
    motus::LogLevel level = motus::LogLevel::Info;
    if (!motus::Logger::parseLevel("warn", level) || level != motus::LogLevel::Warn) {
        std::cerr << "motus::Logger::parseLevel did not round-trip \"warn\"\n";
        return 1;
    }

    const char bytes[] = {'m', 'o', 't', 'u', 's'};
    if (motus::hexDump(bytes, sizeof(bytes)).empty()) {
        std::cerr << "motus::hexDump returned an empty rendering\n";
        return 1;
    }

    std::cout << motus::versionString() << '\n'
              << "parsed level: " << motus::Logger::levelName(level) << '\n';

#ifdef MOTUS_WITH_AMQPCPP
    std::cout << "amqpcpp backend headers reachable\n";
#endif

    return 0;
}
