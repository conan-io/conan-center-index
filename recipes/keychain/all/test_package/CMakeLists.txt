cmake_minimum_required(VERSION 3.12.4)
project(test_package)

find_package(keychain CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} keychain::keychain)
