#include <cstdlib>
#include "cpprest/http_utils.h"


int main() {

    web::http::http_request request;

    request.headers().add(U("Host"), U("foobar"));
    request.headers().add(U("X-Forwarded-Host"), U("baz, qux:57"));

    if (web::http::has_header_value(request.headers(), U("foo"), 42)) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
