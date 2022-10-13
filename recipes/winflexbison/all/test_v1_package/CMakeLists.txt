cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# Flex

set(FLEX_TARGET_COMPILE_FLAGS "")
if(MSVC)
    set(FLEX_TARGET_COMPILE_FLAGS "--wincompat")
endif()

find_package(FLEX REQUIRED)
set(FLEX_VARS
    FLEX_FOUND
    FLEX_EXECUTABLE
    FLEX_LIBRARIES
    FLEX_INCLUDE_DIRS
)

foreach(FLEX_VAR ${FLEX_VARS})
    message("${FLEX_VAR}: ${${FLEX_VAR}}")
    if(NOT ${FLEX_VAR})
        message(WARNING "${FLEX_VAR} NOT FOUND")
    endif()
endforeach()

FLEX_TARGET(TestParser ../test_package/basic_nr.l "${CMAKE_CURRENT_BINARY_DIR}/lexer.cpp" COMPILE_FLAGS "${FLEX_TARGET_COMPILE_FLAGS}")
add_executable(flex_test_package ${FLEX_TestParser_OUTPUTS})
target_compile_features(flex_test_package PRIVATE cxx_std_11)

# Bison

find_package(BISON)

set(BISON_VARS
    BISON_FOUND
    BISON_EXECUTABLE
    BISON_VERSION
)

foreach(BISON_VAR ${BISON_VARS})
    message("${BISON_VAR}: ${${BISON_VAR}}")
    if(NOT ${BISON_VAR})
        message(WARNING "${BISON_VAR} NOT FOUND")
    endif()
endforeach()

bison_target(bison_parser_target ../test_package/mc_parser.yy "${CMAKE_CURRENT_BINARY_DIR}/mc_parser.cpp")

add_executable(bison_test_package "${CMAKE_CURRENT_BINARY_DIR}/mc_parser.cpp" ../test_package/dummy_lex.c)
target_compile_features(bison_test_package PRIVATE cxx_std_11)
target_include_directories(bison_test_package PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
