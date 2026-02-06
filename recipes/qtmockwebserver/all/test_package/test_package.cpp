#include <qtmockwebserver/QtMockWebServer.h>

int main(void)
{
    QtMockWebServer s{};

    s.play();

    return EXIT_SUCCESS;
}
