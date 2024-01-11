#include <opencv2/reg/mapprojec.hpp>

int main() {
    cv::reg::MapProjec map;
    map.scale(5.5);
    map.inverseMap();
    map.normalize();
    return 0;
}
