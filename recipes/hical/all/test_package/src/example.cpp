#include <hical/core/Router.h>
#include <iostream>

int main()
{
    hical::Router router;
    router.get("/test", [](const hical::HttpRequest&) -> hical::HttpResponse {
        return hical::HttpResponse::ok("test");
    });
    std::cout << "Hical package test OK" << std::endl;
    return 0;
}
