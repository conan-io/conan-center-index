cmake_minimum_required(VERSION 3.13.4)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(LLVM REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

if(TARGET LLVMInterpreter)  # static libraries
    target_link_libraries(${PROJECT_NAME} PRIVATE
        LLVMInterpreter
        LLVMIRReader
        LLVMX86CodeGen
    )
else()  # shared library
    target_link_libraries(${PROJECT_NAME} LLVM)
endif()
