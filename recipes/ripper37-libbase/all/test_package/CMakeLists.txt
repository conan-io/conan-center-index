cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# Required core lib and optional modules
find_package(libbase CONFIG REQUIRED OPTIONAL_COMPONENTS net win wx)

add_executable(${PROJECT_NAME} test_package.cpp)

# Required core target
target_link_libraries(${PROJECT_NAME} PRIVATE libbase::libbase)
# Optional module targets
if(TARGET libbase::libbase_net)
  target_link_libraries(${PROJECT_NAME} PRIVATE libbase::libbase_net)
endif()
if(TARGET libbase::libbase_win)
  target_link_libraries(${PROJECT_NAME} PRIVATE libbase::libbase_win)
endif()
if(TARGET libbase::libbase_wx)
  target_link_libraries(${PROJECT_NAME} PRIVATE libbase::libbase_wx)
endif()
