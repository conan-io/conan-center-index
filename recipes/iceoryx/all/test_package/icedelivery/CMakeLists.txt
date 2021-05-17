# Copyright (c) 2019 - 2020 by Robert Bosch GmbH. All rights reserved.
# Copyright (c) 2020 - 2021 by Apex.AI Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# Build icedelivery example

cmake_minimum_required(VERSION 3.5)

find_package(iceoryx REQUIRED)

add_executable(iox-cpp-publisher ./iox_publisher.cpp)
target_link_libraries(iox-cpp-publisher
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-publisher-untyped ./iox_publisher_untyped.cpp)
target_link_libraries(iox-cpp-publisher-untyped
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-subscriber ./iox_subscriber.cpp)
target_link_libraries(iox-cpp-subscriber
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-subscriber-untyped ./iox_subscriber_untyped.cpp)
target_link_libraries(iox-cpp-subscriber-untyped
    iceoryx_posh::iceoryx_posh
)

set_target_properties(iox-cpp-subscriber iox-cpp-subscriber-untyped
                      iox-cpp-publisher iox-cpp-publisher-untyped
                      PROPERTIES
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)
