cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(onnxruntime REQUIRED CONFIG)
add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/test_package.cpp)
if(WITH_CUDA)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_CUDA)
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE onnxruntime::onnxruntime)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(WIN32 AND DEFINED CONAN_BIN_DIRS_ONNXRUNTIME AND EXISTS ${CONAN_BIN_DIRS_ONNXRUNTIME})
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CONAN_BIN_DIRS_ONNXRUNTIME}
        $<TARGET_FILE_DIR:${PROJECT_NAME}>
    )
endif()
