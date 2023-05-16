cmake_minimum_required(VERSION 3.5)
project(test_package C)

find_package(libnl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libnl::nl libnl::nl-route libnl::nl-genl libnl::nl-nf libnl::nl-cli libnl::nl-idiag)
