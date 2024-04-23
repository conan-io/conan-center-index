#include <osrm/coordinate.hpp>
#include <osrm/engine_config.hpp>
#include <osrm/json_container.hpp>
#include <osrm/osrm.hpp>
#include <osrm/route_parameters.hpp>

int main()
{
    using namespace osrm;
    RouteParameters params;
    params.coordinates.push_back({util::FloatLongitude{7.419758}, util::FloatLatitude{43.731142}});
    engine::api::ResultT result = json::Object();
}
