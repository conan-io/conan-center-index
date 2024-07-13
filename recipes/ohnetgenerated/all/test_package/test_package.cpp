#include <OpenHome/Net/Core/DvUpnpOrgDimming1.h>
#include <OpenHome/Net/Core/OhNet.h>
#include <memory>

using namespace OpenHome::Net;

class Dimming : public DvProviderUpnpOrgDimming1 {
public:
  Dimming(DvDevice &aDevice) : DvProviderUpnpOrgDimming1(aDevice) {
    EnablePropertyLoadLevelStatus();
    EnablePropertyStepDelta();
    EnablePropertyRampRate();
    EnablePropertyIsRamping();
    EnablePropertyRampPaused();
  };
};

int main() {
  InitialisationParams *initParams = InitialisationParams::Create();
  auto library = new Library(initParams);
  auto dvStack = library->StartDv();
  OpenHome::Bws<12> udn;
  udn.Append("test-dimming");
  DvDeviceStandard *device = new DvDeviceStandard(*dvStack, udn);

  device->SetAttribute("Upnp.Domain", "av.openhome.org");
  auto dimming = new Dimming(*device);
  dimming->SetPropertyIsRamping(true);
  OpenHome::TBool isRamping;
  dimming->GetPropertyIsRamping(isRamping);
  ASSERT(isRamping == true);
}
