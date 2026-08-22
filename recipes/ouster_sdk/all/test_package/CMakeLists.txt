cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OusterSDK REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if (OUSTER_SDK_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE OusterSDK::shared_library)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE OusterSDK::ouster_client
        $<$<TARGET_EXISTS:OusterSDK::ouster_pcap>:OusterSDK::ouster_pcap>
        $<$<TARGET_EXISTS:OusterSDK::ouster_osf>:OusterSDK::ouster_osf>
        $<$<TARGET_EXISTS:OusterSDK::ouster_viz>:OusterSDK::ouster_viz>
        $<$<TARGET_EXISTS:OusterSDK::ouster_sensor>:OusterSDK::ouster_sensor>
        $<$<TARGET_EXISTS:OusterSDK::ouster_mapping>:OusterSDK::ouster_mapping>
    )
endif()
