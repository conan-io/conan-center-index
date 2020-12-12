cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

if(NOT HEADER_ONLY)
    if(WITH_RANDOM)
        find_package(Boost COMPONENTS random REQUIRED)
        add_executable(random_exe random.cpp)
        target_link_libraries(random_exe PRIVATE Boost::random)
    endif()

    if(WITH_REGEX)
        find_package(Boost COMPONENTS regex REQUIRED)
        add_executable(regex_exe regex.cpp)
        target_link_libraries(regex_exe PRIVATE Boost::regex)
    endif()

    if(WITH_TEST)
        find_package(Boost COMPONENTS unit_test_framework REQUIRED)
        add_executable(test_exe test.cpp)
        target_link_libraries(test_exe PRIVATE Boost::unit_test_framework)
    endif()

    if(WITH_COROUTINE)
        find_package(Boost COMPONENTS coroutine REQUIRED)
        add_executable(coroutine_exe coroutine.cpp)
        target_link_libraries(coroutine_exe PRIVATE Boost::coroutine)
    endif()

    if(WITH_CHRONO)
        find_package(Boost COMPONENTS chrono REQUIRED)
        add_executable(chrono_exe chrono.cpp)
        target_link_libraries(chrono_exe PRIVATE Boost::chrono)
    endif()

    if(WITH_PYTHON)
        find_package(Boost COMPONENTS python REQUIRED)
        add_library(hello_ext MODULE python.cpp)
        set_property(TARGET hello_ext PROPERTY PREFIX "")

        find_package(PythonInterp REQUIRED)
        find_package(PythonLibs REQUIRED)

        target_include_directories(hello_ext PRIVATE ${PYTHON_INCLUDE_DIRS})
        target_link_libraries(hello_ext PRIVATE Boost::python${PYTHON_COMPONENT_SUFFIX} ${PYTHON_LIBRARIES})
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
        endif()

        add_executable(numpy_exe numpy.cpp)
        target_include_directories(numpy_exe PRIVATE ${PYTHON_INCLUDE_DIRS})
        target_link_libraries(numpy_exe PRIVATE Boost::numpy${PYTHON_COMPONENT_SUFFIX} ${PYTHON_LIBRARIES})
    endif()
endif()

# Test header-only target
find_package(Boost REQUIRED)
add_executable(lambda_exe lambda.cpp)
target_link_libraries(lambda_exe PRIVATE Boost::headers)
