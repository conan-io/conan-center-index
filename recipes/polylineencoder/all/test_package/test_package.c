#include <stdio.h>

#include <polylineencoder/polylineencoder.h>

int main(int argc, char *argv[]) {
    gepaf::PolylineEncoder encoder;
    encoder.addPoint(38.5, -120.2);
    encoder.addPoint(40.7, -120.95);
    encoder.addPoint(43.252, -126.453);

    if (encoder.encode() != "_p~iF~ps|U_ulLnnqC_mqNvxq`@")
    {
        return -1;
    }

    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mqNvxq`@");
    if (!(decodedPolyline.size() == 3 &&
        decodedPolyline[0] == gepaf::PolylineEncoder::Point(38.5, -120.2) &&
        decodedPolyline[1] == gepaf::PolylineEncoder::Point(40.7, -120.95) &&
        decodedPolyline[2] == gepaf::PolylineEncoder::Point(43.252, -126.453)))
    {
        return -1;
    }

    return 0;
}
