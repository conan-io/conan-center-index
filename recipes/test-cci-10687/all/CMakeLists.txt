cmake_minimum_required(VERSION 3.15)
project(test-cci-10687 CXX)

find_package(Fontconfig)

add_executable(test-cci-10687 src/test-cci-10687.cpp src/main.cpp)
target_include_directories(test-cci-10687 PUBLIC include)

target_link_libraries(test-cci-10687 PUBLIC Fontconfig::Fontconfig)

install(TARGETS test-cci-10687)
