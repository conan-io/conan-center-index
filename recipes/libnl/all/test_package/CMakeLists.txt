cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

include(FindPkgConfig)

find_package(libnl REQUIRED CONFIG)

find_package(PkgConfig REQUIRED)
pkg_check_modules(libnl-3.0 REQUIRED IMPORTED_TARGET libnl-3.0)
pkg_check_modules(libnl-route-3.0 REQUIRED IMPORTED_TARGET libnl-route-3.0)
pkg_check_modules(libnl-genl-3.0 REQUIRED IMPORTED_TARGET libnl-genl-3.0)
pkg_check_modules(libnl-nf-3.0 REQUIRED IMPORTED_TARGET libnl-nf-3.0)
pkg_check_modules(libnl-cli-3.0 REQUIRED IMPORTED_TARGET libnl-cli-3.0)
pkg_check_modules(libnl-idiag-3.0 REQUIRED IMPORTED_TARGET libnl-idiag-3.0)
pkg_check_modules(libnl-xfrm-3.0 QUIET IMPORTED_TARGET libnl-xfrm-3.0)

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libnl::nl libnl::nl-route libnl::nl-genl libnl::nl-nf libnl::nl-cli libnl::nl-idiag $<$<TARGET_EXISTS:libnl::nl-xfrm>:libnl::nl-xfrm>)
