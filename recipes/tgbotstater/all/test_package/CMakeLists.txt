cmake_minimum_required(VERSION 3.7.0)
project(test_package)

find_package(TgBotStater REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${tgbotstater_LIBRARIES})
