cmake_minimum_required(VERSION 3.1)
project(test_package)
enable_testing()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

conan_basic_setup()

if(NOT HEADER_ONLY)
    set(boost_components)
    if(WITH_COROUTINE)
        list(APPEND boost_components coroutine)
        list(APPEND boost_components thread)
    endif()
    if(WITH_PYTHON)
        list(APPEND boost_components python${WITH_PYTHON_VERSION})
    endif()
    if(WITH_RANDOM)
        list(APPEND boost_components random)
    endif()
    if(WITH_REGEX)
        list(APPEND boost_components regex)
    endif()
    if(WITH_CHRONO)
        list(APPEND boost_components chrono)
    endif()
    if(WITH_TEST)
        list(APPEND boost_components unit_test_framework)
    endif()

    find_package(Boost COMPONENTS ${boost_components} REQUIRED)

    if(WITH_RANDOM)
        add_executable(random_exe random.cpp)
        target_link_libraries(random_exe Boost::random ${CONAN_SYSTEM_LIBS_BOOST})
    endif()

    if(WITH_REGEX)
        add_executable(regex_exe regex.cpp)
        target_link_libraries(regex_exe Boost::regex ${CONAN_SYSTEM_LIBS_BOOST})
        add_test(NAME TestRegex
            COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>" ${TEST_ARGS})
    endif()

    if(WITH_TEST)
        add_executable(test_exe test.cpp)
        target_link_libraries(test_exe Boost::unit_test_framework ${CONAN_SYSTEM_LIBS_BOOST})
    endif()

    if(WITH_COROUTINE)
        add_executable(coroutine_exe coroutine.cpp)
        target_link_libraries(coroutine_exe Boost::coroutine Boost::thread ${CONAN_SYSTEM_LIBS_BOOST})
    endif()

    if(WITH_CHRONO)
        add_executable(chrono_exe chrono.cpp)
        target_link_libraries(chrono_exe Boost::chrono ${CONAN_SYSTEM_LIBS_BOOST})
    endif()

    if(WITH_PYTHON)
        find_package(Python ${WITH_PYTHON_VERSION} COMPONENTS Development REQUIRED)
        target_link_libraries(Boost::python${WITH_PYTHON_VERSION} INTERFACE Python::Python)

        add_library(hello_ext SHARED python.cpp)
        target_link_libraries(hello_ext Boost::python${WITH_PYTHON_VERSION} ${CONAN_SYSTEM_LIBS_BOOST})
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
        else()
            set_target_properties(hello_ext PROPERTIES PREFIX "")
        endif()
    endif()
endif()

add_executable(lambda_exe lambda.cpp)
target_link_libraries(lambda_exe ${CONAN_SYSTEM_LIBS_BOOST})
add_test(NAME TestLambda
    COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda_exe>" ${TEST_ARGS})
