cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cli REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cli::cli)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

find_package(asio REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_asio test_package_asio.cpp)
target_link_libraries(${PROJECT_NAME}_asio PRIVATE cli::cli asio::asio)
target_compile_features(${PROJECT_NAME}_asio PRIVATE cxx_std_14)
target_compile_definitions(${PROJECT_NAME}_asio PRIVATE CLI_EXAMPLES_USE_STANDALONEASIO_SCHEDULER)

find_package(Boost REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_boost test_package_asio.cpp)
target_link_libraries(${PROJECT_NAME}_boost PRIVATE cli::cli Boost::system)
target_compile_features(${PROJECT_NAME}_boost PRIVATE cxx_std_14)
target_compile_definitions(${PROJECT_NAME}_boost PRIVATE CLI_EXAMPLES_USE_BOOSTASIO_SCHEDULER)
