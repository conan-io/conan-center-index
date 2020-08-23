#include <cstdlib>
#include <iostream>
#include <Wt/WLength.h>
#include <Wt/WServer.h>

#ifdef WITH_DBO

#include <Wt/Dbo/Dbo.h>

#endif


int main(int argc, char** argv)
{
    Wt::WLength l("10px");
#ifdef WITH_DBO
    Wt::Dbo::Session session;
#endif

    Wt::WServer server(argc, argv, WTHTTP_CONFIGURATION);

    return EXIT_SUCCESS;
}
