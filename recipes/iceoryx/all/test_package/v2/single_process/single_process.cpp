// Copyright (c) 2020 - 2021 by Robert Bosch GmbH All rights reserved.
// Copyright (c) 2020 - 2021 by Apex.AI Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

#include "iceoryx_hoofs/cxx/convert.hpp"
#include "iceoryx_hoofs/log/logmanager.hpp"
#include "iceoryx_hoofs/posix_wrapper/signal_watcher.hpp"
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

struct TransmissionData_t
{
    uint64_t counter;
};

constexpr std::chrono::milliseconds CYCLE_TIME{100};

void consoleOutput(const char* source, const char* arrow, const uint64_t counter)
{
    static std::mutex consoleOutputMutex;

    std::lock_guard<std::mutex> lock(consoleOutputMutex);
    std::cout << source << arrow << counter << std::endl;
}

void publisher()
{
    //! [publisher]
    iox::popo::PublisherOptions publisherOptions;
    publisherOptions.historyCapacity = 10U;
    iox::popo::Publisher<TransmissionData_t> publisher({"Single", "Process", "Demo"}, publisherOptions);
    //! [publisher]

    //! [send]
    uint64_t counter{0};
    constexpr const char GREEN_RIGHT_ARROW[] = "\033[32m->\033[m ";
    while (!iox::posix::hasTerminationRequested())
    {
        publisher.loan().and_then([&](auto& sample) {
            sample->counter = counter++;
            consoleOutput("Sending   ", GREEN_RIGHT_ARROW, sample->counter);
            sample.publish();
        });

        std::this_thread::sleep_for(CYCLE_TIME);
    }
    //! [send]
}

void subscriber()
{
    //! [subscriber]
    iox::popo::SubscriberOptions options;
    options.queueCapacity = 10U;
    options.historyRequest = 5U;
    iox::popo::Subscriber<TransmissionData_t> subscriber({"Single", "Process", "Demo"}, options);
    //! [subscriber]

    //! [receive]
    constexpr const char ORANGE_LEFT_ARROW[] = "\033[33m<-\033[m ";
    while (!iox::posix::hasTerminationRequested())
    {
        if (iox::SubscribeState::SUBSCRIBED == subscriber.getSubscriptionState())
        {
            bool hasMoreSamples{true};

            do
            {
                subscriber.take()
                    .and_then([&](auto& sample) { consoleOutput("Receiving ", ORANGE_LEFT_ARROW, sample->counter); })
                    .or_else([&](auto& result) {
                        hasMoreSamples = false;
                        if (result != iox::popo::ChunkReceiveResult::NO_CHUNK_AVAILABLE)
                        {
                            std::cout << "Error receiving chunk." << std::endl;
                        }
                    });
            } while (hasMoreSamples);
        }

        std::this_thread::sleep_for(CYCLE_TIME);
    }
    //! [receive]
}

int main()
{
    // set the log level to error to see the essence of the example
    //! [log level]
    iox::log::LogManager::GetLogManager().SetDefaultLogLevel(iox::log::LogLevel::kError);
    //! [log level]

    //! [roudi config]
    iox::RouDiConfig_t defaultRouDiConfig = iox::RouDiConfig_t().setDefaults();
    iox::roudi::IceOryxRouDiComponents roudiComponents(defaultRouDiConfig);
    //! [roudi config]

    //! [roudi]
    constexpr bool TERMINATE_APP_IN_ROUDI_DTOR_FLAG = false;
    iox::roudi::RouDi roudi(
        roudiComponents.rouDiMemoryManager,
        roudiComponents.portManager,
        iox::roudi::RouDi::RoudiStartupParameters{iox::roudi::MonitoringMode::OFF, TERMINATE_APP_IN_ROUDI_DTOR_FLAG});
    //! [roudi]

    // create a single process runtime for inter thread communication
    //! [runtime]
    iox::runtime::PoshRuntimeSingleProcess runtime("singleProcessDemo");
    //! [runtime]

    //! [run]
    std::thread publisherThread(publisher), subscriberThread(subscriber);

    iox::posix::waitForTerminationRequest();

    publisherThread.join();
    subscriberThread.join();

    std::cout << "Finished" << std::endl;
    //! [run]
}
