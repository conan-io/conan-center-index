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

cmake_minimum_required(VERSION 3.5)

find_package(iceoryx  REQUIRED)

add_executable(iox-cpp-callbacks-publisher ./ice_callbacks_publisher.cpp)
target_link_libraries(iox-cpp-callbacks-publisher
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-callbacks-subscriber ./ice_callbacks_subscriber.cpp)
target_link_libraries(iox-cpp-callbacks-subscriber
    iceoryx_posh::iceoryx_posh
)

add_executable(iox-cpp-callbacks-listener-as-class-member ./ice_callbacks_listener_as_class_member.cpp)
target_link_libraries(iox-cpp-callbacks-listener-as-class-member
    iceoryx_posh::iceoryx_posh
)

set_target_properties(
    iox-cpp-callbacks-listener-as-class-member
    iox-cpp-callbacks-subscriber
    iox-cpp-callbacks-publisher
  PROPERTIES
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)
