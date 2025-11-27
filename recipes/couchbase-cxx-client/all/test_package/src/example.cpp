#include <couchbase/logger.hxx>

int main() {
    couchbase::logger::initialize_console_logger();
    couchbase::logger::set_level(couchbase::logger::log_level::trace);
}
