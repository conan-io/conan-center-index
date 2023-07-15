cmake_minimum_required(VERSION 3.10)

project(test_package)

find_package(netease-im REQUIRED)

add_executable(${PROJECT_NAME} test_package.cc)

set_target_properties(${PROJECT_NAME} PROPERTIES
    BUILD_WITH_INSTALL_RPATH 1
    INSTALL_RPATH "@executable_path"
)

target_link_libraries(${PROJECT_NAME} netease-im::netease-im)
