cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(PhysX REQUIRED PhysX PhysXExtensions CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PhysX::PhysX PhysX::PhysXExtensions)
