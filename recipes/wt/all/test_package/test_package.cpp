#include <cstdlib>
#include <iostream>
#include <Wt/WLength.h>

#ifdef WITH_DBO

#include <Wt/Dbo/Dbo.h>

#endif


int main()
{
    Wt::WLength l("10px");
#ifdef WITH_DBO
    Wt::Dbo::Session session;
#endif

    return EXIT_SUCCESS;
}
