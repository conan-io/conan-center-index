// Proves the package is consumable, without needing a broker.
//
// parseLevel, levelName and hexDump are declared in motus/Logger.hpp and defined in the
// compiled Logger translation unit, so linking this exercises the static library rather
// than just the headers. versionString() comes from motus/Version.hpp, which CMake
// generates at build time -- including it here checks that the generated header was
// installed alongside the hand-written ones.
//
// Nothing below emits a log record, so the logger's sink thread never starts and the
// test stays deterministic on every platform ConanCenter builds.

#include <iostream>

#include <motus/Logger.hpp>
#include <motus/Version.hpp>

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
    return 0;
}
