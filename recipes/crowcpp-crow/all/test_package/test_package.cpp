#ifdef CROW_AMALGAMATION
#include "crow_all.h"
#else
#include "crow.h"
#endif

int main()
{
    crow::SimpleApp app;

    CROW_ROUTE(app, "/")
    ([]() {
        return "Hello world!";
    });

    app.port(18080);
}
