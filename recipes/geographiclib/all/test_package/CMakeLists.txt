cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(geographiclib COMPONENTS GeographicLib CartConvert)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} GeographicLib::GeographicLib)

# Test CMake imported executable target
if(GeographicLib_CartConvert_FOUND)
  set(CARTCONVERT_RESULT ${CMAKE_CURRENT_BINARY_DIR}/cartconvert_result.txt)
  add_custom_target(CartConvert-test DEPENDS ${CARTCONVERT_RESULT})
  add_custom_command(
    COMMENT "Test GeographicLib::CartConvert imported executable target"
    OUTPUT ${CARTCONVERT_RESULT}
    COMMAND GeographicLib::CartConvert
    ARGS --input-string "33.3 44.4 6000" -l 33 44 20 --output-file ${CARTCONVERT_RESULT}
  )
  add_dependencies(${PROJECT_NAME} CartConvert-test)
endif()
