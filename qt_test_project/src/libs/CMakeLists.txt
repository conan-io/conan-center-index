cmake_minimum_required(VERSION 3.15)
project(${LIBRARY_NAME} CXX)

# ==============================================
# Targets

set(LIBRARY_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/my_lib.cpp")
set(LIBRARY_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/include/my_lib/my_lib.hpp")
set(LIBRARY_INCLUDES "${CMAKE_CURRENT_SOURCE_DIR}/include"
                     "${CMAKE_BINARY_DIR}/configured_files/include")

add_library(${LIBRARY_NAME} STATIC ${LIBRARY_SOURCES} ${LIBRARY_HEADERS})

target_include_directories(
    ${LIBRARY_NAME}
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
           $<INSTALL_INTERFACE:include>)

target_compile_options(${LIBRARY_NAME} PUBLIC -Wall -Wextra -Wpedantic)

target_compile_features(${LIBRARY_NAME} PUBLIC cxx_std_17)

target_link_libraries(${LIBRARY_NAME} 
PRIVATE 
    spdlog::spdlog
    nlohmann_json::nlohmann_json
)