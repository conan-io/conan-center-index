project(testcpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(testcpp test.cpp)
target_link_libraries(testcpp daggy::daggy)