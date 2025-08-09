#include <iostream>
#include "GeoLite2PP.hpp"

int main(void) {
    try {
        GeoLite2PP::DB db("dummy.mmdb");
        std::cout << "maxmind library : " << db.get_lib_version_mmdb() << '\n';
        std::cout << "GeoLite2++ library : " << db.get_lib_version_geolite2pp() << '\n';
    } catch (std::system_error& ex) {
        std::cout << ex.what() << '\n';
    }
    return 0;
}
