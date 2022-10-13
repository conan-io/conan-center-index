cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

find_package(PkgConfig)
pkg_check_modules(LDNS REQUIRED "ldns")

add_executable(example example.c)
target_include_directories(example PUBLIC ${LDNS_INCLUDE_DIRS})
target_link_libraries(example PUBLIC ${LDNS_LDFLAGS})
