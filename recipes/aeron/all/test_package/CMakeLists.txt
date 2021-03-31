cmake_minimum_required(VERSION 3.6.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Threads REQUIRED)

# platform specific flags
if (APPLE)
    add_compile_options(-Wsign-compare)
    add_definitions(-DDarwin)
    add_compile_options(-Wno-deprecated-register)
elseif (CYGWIN)
    add_definitions(-DWIN32)
    if (AERON_TESTS)
        add_definitions(-DGTEST_HAS_PTHREAD)
    endif ()
    set(CMAKE_CXX_EXTENSIONS ON)
elseif (MSVC)
    add_definitions(-DWIN32)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-D_CRT_NONSTDC_NO_WARNINGS)
    add_definitions(-DNOMINMAX)

    if (${MSVC_VERSION} GREATER_EQUAL 1915)
        # Acknowledge that we understand MSVC resolved a byte alignment issue in this compiler
        add_definitions(-D_ENABLE_EXTENDED_ALIGNED_STORAGE)
    endif ()

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MTd /Od /Zi /MP /wd4251")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MT /MP /wd4251")

    unset(CMAKE_C_STANDARD) # To avoid `/std:c11` in the compiler options

    if (C_WARNINGS_AS_ERRORS)
        add_compile_options($<$<COMPILE_LANGUAGE:C>:/WX>)
    endif (C_WARNINGS_AS_ERRORS)

    if (CXX_WARNINGS_AS_ERRORS)
        add_compile_options($<$<COMPILE_LANGUAGE:CXX>:/WX>)
    endif (CXX_WARNINGS_AS_ERRORS)
endif ()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} ${CMAKE_THREAD_LIBS_INIT})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
