# Copyright (c) 2021 by Apex.AI Inc. All rights reserved.
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

# Build icehello example

cmake_minimum_required(VERSION 3.5)

find_package(iceoryx REQUIRED)

add_executable(iox-cpp-publisher-helloworld ./iox_publisher_helloworld.cpp)
target_link_libraries(iox-cpp-publisher-helloworld
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-subscriber-helloworld ./iox_subscriber_helloworld.cpp)
target_link_libraries(iox-cpp-subscriber-helloworld
    iceoryx_posh::iceoryx_posh
)

set_target_properties(iox-cpp-subscriber-helloworld iox-cpp-publisher-helloworld
                      PROPERTIES
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)

# ========================================================== //

install(TARGETS iox-cpp-publisher-helloworld iox-cpp-subscriber-helloworld
        RUNTIME DESTINATION bin)
