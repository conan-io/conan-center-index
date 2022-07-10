#include <xtr/logger.hpp>

int main()
{
    xtr::logger log;
    auto s = log.get_sink("Test");
    XTR_LOG(s, "Hello world");
    return 0;
}
