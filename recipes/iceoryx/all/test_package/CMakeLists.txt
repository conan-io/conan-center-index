cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(iceoryx REQUIRED CONFIG)

add_executable(single_process single_process/single_process.cpp)
target_link_libraries(single_process iceoryx_posh::iceoryx_posh_roudi iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-publisher icedelivery/iox_publisher.cpp)
target_link_libraries(iox-cpp-publisher iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-publisher-untyped icedelivery/iox_publisher_untyped.cpp)
target_link_libraries(iox-cpp-publisher-untyped iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-subscriber icedelivery/iox_subscriber.cpp)
target_link_libraries(iox-cpp-subscriber iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-subscriber-untyped icedelivery/iox_subscriber_untyped.cpp)
target_link_libraries(iox-cpp-subscriber-untyped iceoryx_posh::iceoryx_posh)

add_executable(iox-c-publisher icedelivery_in_c/ice_c_publisher.c)
set_source_files_properties(icedelivery_in_c/ice_c_publisher.c PROPERTIES LANGUAGE C)
target_link_libraries(iox-c-publisher iceoryx_binding_c::iceoryx_binding_c)

add_executable(iox-c-subscriber icedelivery_in_c/ice_c_subscriber.c)
set_source_files_properties(icedelivery_in_c/ice_c_subscriber.c PROPERTIES LANGUAGE C)
target_link_libraries(iox-c-subscriber iceoryx_binding_c::iceoryx_binding_c)
