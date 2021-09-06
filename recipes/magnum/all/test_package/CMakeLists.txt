cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Magnum REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Magnum::Magnum)


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
