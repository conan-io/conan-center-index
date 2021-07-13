#include "stdlib.h"
#include "PcapLiveDeviceList.h"

int main() {
    const std::vector<pcpp::PcapLiveDevice*>& devList =
    pcpp::PcapLiveDeviceList::getInstance().getPcapLiveDevicesList();
    if (devList.size() > 0) {
        if (devList[0]->getName() == NULL)
            return 1;
        return 0;
    }
    return 0;
}
