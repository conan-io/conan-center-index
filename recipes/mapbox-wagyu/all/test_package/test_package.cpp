#include <cassert>

#include <mapbox/geometry/wagyu/quick_clip.hpp>
#include <mapbox/geometry/wagyu/wagyu.hpp>

int main() {
    mapbox::geometry::point< std::int64_t> p1 = { 0, 0 };
    mapbox::geometry::point< std::int64_t> p2 = { 100, 100 };
    mapbox::geometry::box< std::int64_t> bbox(p1, p2);

    mapbox::geometry::linear_ring< std::int64_t> lr;
    lr.push_back(mapbox::geometry::point< std::int64_t>(25, 25));
    lr.push_back(mapbox::geometry::point< std::int64_t>(175, 25));
    lr.push_back(mapbox::geometry::point< std::int64_t>(175, 75));
    lr.push_back(mapbox::geometry::point< std::int64_t>(25, 75));
    lr.push_back(mapbox::geometry::point< std::int64_t>(25, 25));

    auto out = mapbox::geometry::wagyu::quick_clip::quick_lr_clip(lr, bbox);

    mapbox::geometry::linear_ring< std::int64_t> want;
    want.push_back(mapbox::geometry::point< std::int64_t>(25, 25));
    want.push_back(mapbox::geometry::point< std::int64_t>(100, 25));
    want.push_back(mapbox::geometry::point< std::int64_t>(100, 75));
    want.push_back(mapbox::geometry::point< std::int64_t>(25, 75));
    want.push_back(mapbox::geometry::point< std::int64_t>(25, 25));

    assert(out == want);
}
