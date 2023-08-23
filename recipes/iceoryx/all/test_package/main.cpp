
#include "iceoryx_posh/iceoryx_posh_config.hpp"
#include "iceoryx_posh/iceoryx_posh_types.hpp"
#include "iceoryx_posh/internal/roudi/roudi.hpp"
#include "iceoryx_posh/popo/publisher.hpp"
#include "iceoryx_posh/popo/subscriber.hpp"
#include "iceoryx_posh/roudi/iceoryx_roudi_components.hpp"
#include "iceoryx_posh/runtime/posh_runtime_single_process.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <thread>

int main(int argc, char* argv[]) {

    iox::log::LogManager::GetLogManager().SetDefaultLogLevel(iox::log::LogLevel::kInfo);
    iox::RouDiConfig_t defaultRouDiConfig = iox::RouDiConfig_t().setDefaults();

    /* Don't call on test run with conan */
    if(argc >=2) {
      iox::roudi::IceOryxRouDiComponents roudiComponents(defaultRouDiConfig);
    }

    return 0;
}
