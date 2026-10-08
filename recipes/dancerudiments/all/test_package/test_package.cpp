#include <dancerudiments/dance_rudiments.hpp>
#include <cmath>
int main() {
    if (dancerudiments::catalogue().size() != 1731) return 1;
    auto first = dancerudiments::sample("circle", 0);
    auto wrapped = dancerudiments::sample("circle", 64);
    return !(std::isfinite(first.x) && first.x == wrapped.x && first.y == wrapped.y);
}
