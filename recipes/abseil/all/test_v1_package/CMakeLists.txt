cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(absl REQUIRED CONFIG)

# Test components
add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(cxx_std_14 IN_LIST CMAKE_CXX_COMPILE_FEATURES)
    add_executable(${PROJECT_NAME}_14 ../test_package/test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_14 PRIVATE absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
    target_compile_features(${PROJECT_NAME}_14 PRIVATE cxx_std_14)
endif()
if(cxx_std_17 IN_LIST CMAKE_CXX_COMPILE_FEATURES)
    add_executable(${PROJECT_NAME}_17 ../test_package/test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_17 PRIVATE absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
    target_compile_features(${PROJECT_NAME}_17 PRIVATE cxx_std_17)
endif()
# old abseil used std::result_of (which was removed in C++20) https://github.com/abseil/abseil-cpp/issues/649
if(CXX20_SUPPORTED)
    if(cxx_std_20 IN_LIST CMAKE_CXX_COMPILE_FEATURES)
        add_executable(${PROJECT_NAME}_20 ../test_package/test_package.cpp)
        target_link_libraries(${PROJECT_NAME}_20 PRIVATE absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
        target_compile_features(${PROJECT_NAME}_20 PRIVATE cxx_std_20)
    endif()
    if(cxx_std_23 IN_LIST CMAKE_CXX_COMPILE_FEATURES)
        add_executable(${PROJECT_NAME}_23 ../test_package/test_package.cpp)
        target_link_libraries(${PROJECT_NAME}_23 PRIVATE absl::strings absl::flat_hash_map absl::flat_hash_set absl::int128 absl::time)
        target_compile_features(${PROJECT_NAME}_23 PRIVATE cxx_std_23)
    endif()
endif()

# Test also global target
add_executable(${PROJECT_NAME}_global ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME}_global PRIVATE CONAN_PKG::abseil)
target_compile_features(${PROJECT_NAME}_global PRIVATE cxx_std_11)
