cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper LANGUAGES CXX)

find_package(Eigen3 REQUIRED CONFIG)
find_package(fast_double_parser REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)

add_subdirectory(src)

if(_MAJOR_VERSION GREATER_EQUAL 4)
    set(TARGETS lightgbm_objs lightgbm_capi_objs)
    set(VISIBILITY PRIVATE)
else()
    set(TARGETS lightgbm _lightgbm)
    set(VISIBILITY "")
endif()

foreach(target ${TARGETS})
    target_link_libraries(${target} ${VISIBILITY} Eigen3::Eigen fast_double_parser::fast_double_parser fmt::fmt)
endforeach()
