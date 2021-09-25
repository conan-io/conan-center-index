#include <reckless/file_writer.hpp>
#include <reckless/severity_log.hpp>

#include <string>

using log_t = reckless::severity_log<
    reckless::indent<4>,
    ' ',
    reckless::severity_field,
    reckless::timestamp_field
    >;

reckless::file_writer writer("log.txt");
log_t g_log(&writer);

int main()
{
    std::string s("Hello World!");

    g_log.debug("Pointer: %p", s.c_str());
    g_log.info("Info line: %s", s);

    for (int i = 0; i != 4; ++i) {
        reckless::scoped_indent indent;
        g_log.warn("Warning: %d", i);
    }

    g_log.error("Error: %f", 3.14);

    return 0;
}
