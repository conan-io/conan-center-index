cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(plotjuggler_sdk REQUIRED CONFIG)

add_executable(test_package test_package.cpp)
# plugin_sdk transitively pulls in the `base` component (libpj_base.a) and
# nlohmann_json, exercising real linkage — not just header availability.
target_link_libraries(test_package PRIVATE plotjuggler_sdk::plugin_sdk)

# When the package was built with_host (default), also link and exercise the
# host loaders so the plugin_host component's lib list and its `dl` syslib
# wiring are validated. Gated so `-o with_host=False` still builds.
if(TEST_WITH_HOST)
  target_link_libraries(test_package PRIVATE plotjuggler_sdk::plugin_host)
  target_compile_definitions(test_package PRIVATE PJ_TEST_WITH_HOST)
endif()
