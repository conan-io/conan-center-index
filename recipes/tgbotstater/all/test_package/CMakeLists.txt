cmake_minimum_required(VERSION 3.7.0)
project(test_package)

find_package(TgBotStater REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${tgbotstater_LIBRARIES})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
