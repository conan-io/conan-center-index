# SPDX-License-Identifier: MIT Copyright (c) 2022 Jai Bellare See
# <https://opensource.org/licenses/MIT/> or LICENSE.md Project homepage:
# <https://github.com/strangeQuark1041/samarium>

cmake_minimum_required(VERSION 3.16)
project(samarium_tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

find_package(
    SFML
    COMPONENTS system window graphics
    REQUIRED
)
find_package(fmt REQUIRED)

if(NOT WIN32)
    find_package(TBB REQUIRED)
endif()

function(create_test TEST_NAME TEST_SOURCES)
    message(STATUS "Creating test: ${TEST_NAME}, with sources: ${TEST_SOURCES}")

    add_executable(${TEST_NAME} "${TEST_SOURCES}")
    target_include_directories(${TEST_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/src)

    target_link_libraries(${TEST_NAME} PRIVATE samarium::samarium)
    target_link_libraries(${TEST_NAME} PRIVATE fmt::fmt)
    target_link_libraries(${TEST_NAME} PRIVATE sfml-graphics)

    if(NOT WIN32)
        message(STATUS "Linking ${TEST_NAME} with TBB")
        target_link_libraries(${TEST_NAME} PUBLIC TBB::tbb)
    endif()

    if(WARNINGS)
        target_compile_options(samarium_tests PRIVATE ${WARNINGS})
    endif()
endfunction()

function(create_test_with_output_dir TEST_NAME TEST_SOURCES TEST_OUTPUT_DIR)
    create_test(${TEST_NAME} "${TEST_SOURCES}")

    message(STATUS "Setting output directory for ${TEST_NAME} to ${TEST_OUTPUT_DIR}")
    set_target_properties(
        ${TEST_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${TEST_OUTPUT_DIR}"
    )
endfunction()

option(SAMARIUM_BUILD_EXTRA_TESTS "Only run the main program and not the tests" ON)
if(SAMARIUM_BUILD_EXTRA_TESTS)
    create_test(samarium_tests "tests/Vector2.cpp;tests/concepts.cpp;tests/main.cpp")
else()
    create_test(samarium_tests main.cpp)
endif()

option(SAMARIUM_BUILD_EXAMPLES "Build example programs" ON)
if(SAMARIUM_BUILD_EXAMPLES)
    create_test_with_output_dir(
        mandelbrot ../examples/mandelbrot.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        poisson_disk_sampling ../examples/poisson_disk_sampling.cpp
        "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        softbody ../examples/softbody.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        springy_pendulum ../examples/springy_pendulum.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        hilbert_curve ../examples/hilbert_curve.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        fourier_series ../examples/fourier_series.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
    create_test_with_output_dir(
        prime_spiral ../examples/prime_spiral.cpp "${CMAKE_BINARY_DIR}/examples/"
    )
endif()
