#include <embree4/rtcore.h>

#include <iostream>
#include <limits>

int main() {
  RTCDevice device = rtcNewDevice(NULL);
  RTCScene scene = rtcNewScene(device);
  RTCGeometry geom = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_TRIANGLE);

  rtcReleaseGeometry(geom);
  rtcReleaseScene(scene);
  rtcReleaseDevice(device);

  return 0;
}