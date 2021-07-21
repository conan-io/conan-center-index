add_executable(iox-cpp-publisher iox_publisher.cpp)
target_link_libraries(iox-cpp-publisher iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-publisher-untyped iox_publisher_untyped.cpp)
target_link_libraries(iox-cpp-publisher-untyped iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-subscriber iox_subscriber.cpp)
target_link_libraries(iox-cpp-subscriber iceoryx_posh::iceoryx_posh)

add_executable(iox-cpp-subscriber-untyped iox_subscriber_untyped.cpp)
target_link_libraries(iox-cpp-subscriber-untyped iceoryx_posh::iceoryx_posh)
