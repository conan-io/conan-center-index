#include <iostream>
#include <restinio/all.hpp>

using namespace restinio;

int main() {
    // Create express router for our service.
    auto router = std::make_unique<router::express_router_t<>>();
    router->http_get(
            R"(/data/meter/:meter_id(\d+))",
            [](auto req, auto params) {
                const auto qp = parse_query(req->header().query());
                return req->create_response()
                        .set_body(fmt::format("meter_id={}", cast_to<int>(params["meter_id"])))
                        .done();
            });

	std::cout << "success\n";

    return 0;
}
