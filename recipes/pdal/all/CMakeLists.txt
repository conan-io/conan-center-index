cmake_minimum_required(VERSION 3.13)
project(cmake_wrapper)

macro(custom_find_package name)
    find_package(${name} ${ARGN})
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND ${${name}_FOUND})
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

# Unvendored dependencies
find_package(h3 REQUIRED CONFIG)
set(PDAL_H3_LIB_NAME h3::h3)

find_package(Eigen3 REQUIRED CONFIG)
link_libraries(Eigen3::Eigen)

find_package(nanoflann REQUIRED CONFIG)
link_libraries(nanoflann::nanoflann)

find_package(nlohmann_json REQUIRED CONFIG)
link_libraries(nlohmann_json::nlohmann_json)
include_directories(BEFORE src/vendor/nlohmann)

find_package(nlohmann_json_schema_validator REQUIRED CONFIG)
set(JSON_SCHEMA_LIB_NAME nlohmann_json_schema_validator)
link_libraries(nlohmann_json_schema_validator)

find_package(utf8cpp REQUIRED CONFIG)
set(UTFCPP_INCLUDE_DIR ${utf8cpp_INCLUDE_DIR})
set(UTFCPP_LIB_NAME utf8::cpp)

# Use custom_find_package to ensure that the dependency vars use compatible capitalization
custom_find_package(GDAL REQUIRED CONFIG)
custom_find_package(GeoTIFF REQUIRED MODULE)
custom_find_package(LibLZMA CONFIG)
custom_find_package(LibXml2 QUIET MODULE)
custom_find_package(Libunwind QUIET CONFIG)
custom_find_package(ZLIB QUIET CONFIG)
custom_find_package(proj REQUIRED CONFIG)
custom_find_package(zstd QUIET CONFIG)

add_subdirectory(src)
