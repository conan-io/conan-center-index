/*
MIT License

Copyright (c) 2017 Vahan Aghajanyan <vahancho@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <limits>
#include "polylineencoder/polylineencoder.h"

static bool operator==(const gepaf::PolylineEncoder::Point& l, const gepaf::PolylineEncoder::Point& r)
{
    return std::abs(l.longitude() - r.longitude()) < std::numeric_limits<double>::epsilon()
        && std::abs(l.latitude() - r.latitude()) < std::numeric_limits<double>::epsilon();
}

static bool operator!=(const gepaf::PolylineEncoder::Point& l, const gepaf::PolylineEncoder::Point& r)
{
    return !(l == r);
}

static bool test(const std::string &testName,
                 const gepaf::PolylineEncoder &encoder,
                 const std::string &expected)
{
    auto res = encoder.encode();
    if (res == expected) {
        // Decode back.
        auto decodedPolyline = encoder.decode(res);
        const auto &polyline = encoder.polyline();
        if (decodedPolyline.size() != polyline.size())
        {
            fprintf(stderr, "%s fails\n", testName.c_str());
            fprintf(stderr, "\tDecode error: incorrect number of points: '%d' instead of '%d'\n",
                    static_cast<int>(decodedPolyline.size()),
                    static_cast<int>(polyline.size()));
            return false;
        }

        // Compare polylines - they should be equal.
        for (size_t i = 0; i < polyline.size(); ++i)
        {
            const auto &p1 = polyline.at(i);
            const auto &p2 = decodedPolyline.at(i);
            if (p1 != p2)
            {
                fprintf(stderr, "%s fails\n", testName.c_str());
                fprintf(stderr, "\tDecode error: decoded points are different\n");
                return false;
            }
        }

        return true;
    }

    fprintf(stderr, "%s fails\n", testName.c_str());
    fprintf(stderr, "\tExpected: '%s', got: '%s'\n", expected.c_str(), res.c_str());
    return false;
}

static bool test1()
{
    gepaf::PolylineEncoder encoder;
    encoder.addPoint(.0, .0);

    return test(__FUNCTION__, encoder, "??");
}

static bool test2()
{
    gepaf::PolylineEncoder encoder;

    // Poles and equator.
    encoder.addPoint(-90.0, -180.0);
    encoder.addPoint(.0, .0);
    encoder.addPoint(90.0, 180.0);

    return test(__FUNCTION__, encoder, "~bidP~fsia@_cidP_gsia@_cidP_gsia@");
}

static bool test3()
{
    // Empty list of points.
    gepaf::PolylineEncoder encoder;

    return test(__FUNCTION__, encoder, std::string());
}

static bool test4()
{
    // Coordinates from https://developers.google.com/maps/documentation/utilities/polylinealgorithm
    gepaf::PolylineEncoder encoder;
    encoder.addPoint(38.5, -120.2);
    encoder.addPoint(40.7, -120.95);
    encoder.addPoint(43.252, -126.453);

    return test(__FUNCTION__, encoder, "_p~iF~ps|U_ulLnnqC_mqNvxq`@");
}

static bool test5()
{
    // Decode a valid polyline string.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mqNvxq`@");
    if (decodedPolyline.size() == 3 &&
        decodedPolyline[0] == gepaf::PolylineEncoder::Point(38.5, -120.2) &&
        decodedPolyline[1] == gepaf::PolylineEncoder::Point(40.7, -120.95) &&
        decodedPolyline[2] == gepaf::PolylineEncoder::Point(43.252, -126.453)) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test6()
{
    // String too short, last byte missing makes last coordinate invalid.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mqNvxq`");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test7()
{
    // String too short, last bytes missing makes last coordinate.lon missing.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mqN");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test8()
{
    // String too short, last coordinate.lon missing and last coordinate.lat invalid.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mq");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test9()
{
    // String too short, last coordinate.lon missing and last coordinate.lat invalid.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|U_ulLnnqC_mq");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test10()
{
    // Third byte changed from '~' to ' ', generating an invalid fourth coordinate.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p iF~ps|U_ulLnnqC_mqNvxq`@");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test11()
{
    // Fifth byte changed from 'F' to 'f' changing the 'next byte' flag in it,
    // leading to an extremely large latitude for the first coordinate.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~if~ps|U_ulLnnqC_mqNvxq`@");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test12()
{
    // Tenth byte changed from 'U' to 'u' changing the 'next byte' flag in it,
    // leading to an extremely large longitude for the first coordinate.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("_p~iF~ps|u_ulLnnqC_mqNvxq`@");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test13()
{
    // Empty string.
    auto decodedPolyline = gepaf::PolylineEncoder::decode("");
    if (decodedPolyline.size() == 0) {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test14()
{
    // Avoid cumulated error
    gepaf::PolylineEncoder encoder;
    encoder.addPoint(0.0000005, 0.0000005);
    encoder.addPoint(0.0000000, 0.0000000);

    // Intentionally not use test() function as the precision cut generates difference between encode and decode
    // Expectation comes from https://developers.google.com/maps/documentation/utilities/polylineutility
    if (encoder.encode() == "????") {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

static bool test15()
{
    // Avoid cumulated error
    gepaf::PolylineEncoder encoder;
    encoder.addPoint(47.231174468994141, 16.62629508972168);
    encoder.addPoint(47.231208801269531, 16.626440048217773);

    // Intentionally not use test() function as the precision cut generates difference between encode and decode
    // Expectation comes from https://developers.google.com/maps/documentation/utilities/polylineutility
    if (encoder.encode() == "yyg_HkindBG[") {
        return true;
    } else {
        fprintf(stderr, "%s: fails\n", __FUNCTION__);
        return false;
    }
}

int main(int, char**)
{
    printf("Start PolylineEncoder tests\n");

    bool ok = test1();
    ok = test2() && ok;
    ok = test3() && ok;
    ok = test4() && ok;
    ok = test5() && ok;
    ok = test6() && ok;
    ok = test7() && ok;
    ok = test8() && ok;
    ok = test9() && ok;
    ok = test10() && ok;
    ok = test11() && ok;
    ok = test12() && ok;
    ok = test13() && ok;
    ok = test14() && ok;
    ok = test15() && ok;

    printf("PolylineEncoder tests %s\n", ok ? "passed" : "failed");
    return ok ? 0 : 1;
}
