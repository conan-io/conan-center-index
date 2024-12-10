#include <wintls.hpp>

int main(void) {
    boost::wintls::context ctx{boost::wintls::method::system_default};
    return 0;
}
