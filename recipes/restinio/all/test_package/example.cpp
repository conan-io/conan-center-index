#include <iostream>
#include <restinio/all.hpp>

using namespace restinio;

template<typename T>
std::ostream & operator<<(std::ostream & to, const optional_t<T> & v) {
    if(v) to << *v;
    return to;
}

int main() {
    // Create express router for our service.
    auto router = std::make_unique<router::express_router_t<>>();
    router->http_get(
            R"(/data/meter/:meter_id(\d+))",
            [](auto req, auto params) {
                const auto qp = parse_query(req->header().query());
                return req->create_response()
                        .set_body(
                                fmt::format("meter_id={} (year={}/mon={}/day={})",
                                        cast_to<int>(params["meter_id"]),
                                        opt_value<int>(qp, "year"),
                                        opt_value<int>(qp, "mon"),
                                        opt_value<int>(qp, "day")))
                        .done();
            });

	std::cout << "success\n";

    return 0;
}
