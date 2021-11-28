#include <osi3/osi_sensordata.pb.h>

#include <iostream>

int main() {
  
  osi3::SensorData d;
  // Version
  d.mutable_version()->set_version_major(3);
  d.mutable_version()->set_version_minor(2);
  d.mutable_version()->set_version_patch(1);

  void* buffer = malloc(d.ByteSizeLong());
  d.SerializeToArray(buffer, d.ByteSizeLong());
  free(buffer);

  return 0;
}
