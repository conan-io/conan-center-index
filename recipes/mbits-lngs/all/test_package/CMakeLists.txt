cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(mbits-lngs REQUIRED CONFIG)

set(IDL ${CMAKE_CURRENT_SOURCE_DIR}/translations.idl)
set(CPP ${CMAKE_CURRENT_BINARY_DIR}/translations.cpp)
set(HPP ${CMAKE_CURRENT_BINARY_DIR}/translations.hpp)

add_custom_target(
    make_lngs
    COMMAND mbits::lngs res ${IDL} -o ${CPP} --include "translations.hpp"
    COMMAND mbits::lngs enums -r ${IDL} -o ${HPP}
    BYPRODUCTS ${CPP} ${HPP}
    DEPENDS ${IDL}
)

add_executable(${PROJECT_NAME} test_package.cpp ${CPP} ${HPP})
target_link_libraries(${PROJECT_NAME} PRIVATE mbits::liblngs)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
add_dependencies(${PROJECT_NAME} make_lngs)
