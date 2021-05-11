cmake_minimum_required(VERSION 3.1)

set( CMAKE_CXX_STANDARD 14 )

set( CMAKE_CXX_STANDARD_REQUIRED ON )

project(cfgfile.test)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${CMAKE_CURRENT_BINARY_DIR}
    ${CONAN_INCLUDE_DIRS_CFGFILE}/include)

add_custom_target(gencfg
   COMMAND ${CONAN_BIN_DIRS_CFGFILE}/cfgfile.generator${CMAKE_EXECUTABLE_SUFFIX} -i ${CMAKE_CURRENT_SOURCE_DIR}/session_cfg.conf -o ${CMAKE_CURRENT_BINARY_DIR}/cfg.hpp
	)

add_executable(${PROJECT_NAME} example.cpp)

add_dependencies(${PROJECT_NAME} gencfg)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
