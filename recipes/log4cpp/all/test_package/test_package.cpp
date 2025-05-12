#include <cstdlib>
#include "log4cpp/Category.hh"
#include "log4cpp/Appender.hh"
#include "log4cpp/OstreamAppender.hh"


int main(void) {
    log4cpp::OstreamAppender appender("console", &std::cerr);
    log4cpp::Category& root = log4cpp::Category::getRoot();
    root.addAppender(appender);
    root.info("Conan test package");
    root.shutdown();
    return EXIT_SUCCESS;
}
