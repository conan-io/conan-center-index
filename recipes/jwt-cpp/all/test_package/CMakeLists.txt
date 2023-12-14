cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(jwt-cpp REQUIRED CONFIG)
find_package(picojson REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE jwt-cpp::jwt-cpp picojson::picojson)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if (MSVC)
    target_compile_definitions(${PROJECT_NAME} PRIVATE NOMINMAX)
endif()

if (jwt-cpp_VERSION VERSION_GREATER 0.4.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE JSON_TRAITS_NEEDED)
endif()

if (jwt-cpp_VERSION VERSION_GREATER_EQUAL 0.6.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE HAS_DEFAULT_TRAITS)
endif()

if (jwt-cpp_VERSION VERSION_GREATER_EQUAL 0.7.0)
    target_compile_definitions(${PROJECT_NAME} PRIVATE GET_PAYLOAD_JSON)
endif()
