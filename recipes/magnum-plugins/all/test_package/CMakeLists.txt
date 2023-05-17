cmake_minimum_required(VERSION 3.11)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(SHARED_PLUGINS)
    find_package(MagnumPlugins REQUIRED)
else()
    find_package(MagnumPlugins REQUIRED StlImporter)
endif()

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/configure.h.in
               ${CMAKE_CURRENT_BINARY_DIR}/configure.h)

add_executable(${PROJECT_NAME} test_package.cpp)
# Intentionally linking with the global 'MagnumPlugins::MagnumPlugins' target, I want to check it is a valid target (although it might be empty)
target_link_libraries(${PROJECT_NAME} PRIVATE Magnum::Trade MagnumPlugins::MagnumPlugins)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
if(NOT SHARED_PLUGINS)
    target_link_libraries(${PROJECT_NAME} PRIVATE MagnumPlugins::StlImporter)
endif()
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)

if(TARGET_EMSCRIPTEN)
    message("Embed OBJ file")
    set_target_properties(${PROJECT_NAME} 
        PROPERTIES 
            LINK_FLAGS "--embed-file ${CONAN_STL_FILE}@${CONAN_STL_FILE}"
    )
endif()
