cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(cli CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example cli::cli)

target_compile_features(example PRIVATE cxx_std_14)

if (NOT CLI_WITH_ASIO STREQUAL "None")

if (CLI_WITH_ASIO STREQUAL "standalone")
add_compile_definitions(CLI_EXAMPLES_USE_STANDALONEASIO_SCHEDULER)
elseif(CLI_WITH_ASIO STREQUAL "boost")
add_compile_definitions(CLI_EXAMPLES_USE_BOOSTASIO_SCHEDULER)
endif()

add_executable(example_complete example_complete.cpp)
target_link_libraries(example_complete cli::cli)

target_compile_features(example_complete PRIVATE cxx_std_14)

endif()
