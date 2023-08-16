cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(cpuinfo REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if ((${CPUINFO_VERSION} GREATER_EQUAL "20220618") AND (${CPUINFO_VERSION} LESS "20230118"))
    # in that version range cpuinfo exposed cpuinfo::clog. Check that is available through conan recipe
    target_link_libraries(${PROJECT_NAME} PRIVATE cpuinfo::cpuinfo cpuinfo::clog)
else ()
    target_link_libraries(${PROJECT_NAME} PRIVATE cpuinfo::cpuinfo)
endif()

target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
