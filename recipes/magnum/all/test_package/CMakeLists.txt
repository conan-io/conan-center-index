cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(SHARED_PLUGINS)
    find_package(Magnum REQUIRED CONFIG)
else()
    find_package(Magnum REQUIRED ObjImporter CONFIG)
endif()

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/configure.h.in
               ${CMAKE_CURRENT_BINARY_DIR}/configure.h)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Magnum::Magnum Magnum::Trade)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
if(NOT SHARED_PLUGINS)
    target_link_libraries(${PROJECT_NAME} PRIVATE Magnum::ObjImporter)
endif()
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)


# Run some executables (we can only be sure they exist if native build)
if (EXEC_GL_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::gl-info
        ARGS "--help"
        COMMENT "Running magnum-gl-info"
    )
endif()

if (EXEC_AL_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::al-info
        ARGS "--help"
        COMMENT "Running magnum-al-info"
    )
endif()

if (EXEC_DISTANCEFIELDCONVERTER_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::distancefieldconverter
        ARGS "--help"
        COMMENT "Running magnum-distancefieldconverter"
    )
endif()

if (EXEC_FONTCONVERTER_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::fontconverter
        ARGS "--help"
        COMMENT "Running magnum-fontconverter"
    )
endif()

if (EXEC_IMAGECONVERTER_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::imageconverter
        ARGS "--help"
        COMMENT "Running magnum-imageconverter"
    )
endif()

if (EXEC_SCENECONVERTER_INFO AND NOT CMAKE_CROSSCOMPILING)
    add_custom_command(
        TARGET ${PROJECT_NAME} PRE_BUILD
        COMMAND Magnum::sceneconverter
        ARGS "--help"
        COMMENT "Running magnum-sceneconverter"
    )
endif()
