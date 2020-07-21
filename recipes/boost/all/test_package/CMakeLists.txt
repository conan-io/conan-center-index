cmake_minimum_required(VERSION 3.5)
project(test_package)
enable_testing()

set(Boost_DEBUG 1)
include("${CONAN_INSTALL_FOLDER}/conanbuildinfo.cmake")

if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

CONAN_BASIC_SETUP()

IF(NOT HEADER_ONLY)
    set(boost_components)
    if (WITH_COROUTINE)
        list(APPEND boost_components coroutine)
        list(APPEND boost_components thread)
    endif()
    if (WITH_PYTHON)
        find_package(PythonInterp REQUIRED)
        find_package(PythonLibs REQUIRED)
        list(APPEND boost_components "python${PYTHON_COMPONENT_SUFFIX}")

        list(APPEND boost_components "numpy${PYTHON_COMPONENT_SUFFIX}")
    endif()
    if (WITH_RANDOM)
        list(APPEND boost_components random)
    endif()
    if (WITH_REGEX)
        list(APPEND boost_components regex)
    endif()
    if (WITH_CHRONO)
        list(APPEND boost_components chrono)
    endif()

    find_package(Boost COMPONENTS ${boost_components} REQUIRED)

    include_directories(${Boost_INCLUDE_DIRS})

    MESSAGE("LIBS=> ${CONAN_LIBS}")

    if (WITH_RANDOM)
        ADD_EXECUTABLE(random_exe random.cpp)
        TARGET_LINK_LIBRARIES(random_exe Boost::random)
    endif()
    if (WITH_REGEX)
        ADD_EXECUTABLE(regex_exe regex.cpp)
        TARGET_LINK_LIBRARIES(regex_exe Boost::regex)
    endif()

    if (WITH_TEST)
        ADD_EXECUTABLE(test_exe test.cpp)
        TARGET_LINK_LIBRARIES(test_exe Boost::unit_test_framework)
    endif()

    if (WITH_COROUTINE)
        ADD_EXECUTABLE(coroutine_exe coroutine.cpp)
        TARGET_LINK_LIBRARIES(coroutine_exe Boost::coroutine)
    endif()

    if (WITH_CHRONO)
        ADD_EXECUTABLE(chrono_exe chrono.cpp)
        TARGET_LINK_LIBRARIES(chrono_exe Boost::chrono)
    endif()

    if(WITH_PYTHON)
        add_library(hello_ext MODULE python.cpp)
        set_property(TARGET hello_ext PROPERTY PREFIX "")
        target_include_directories(hello_ext PRIVATE ${PYTHON_INCLUDE_DIRS})
        target_link_libraries(hello_ext Boost::python${PYTHON_COMPONENT_SUFFIX} ${PYTHON_LIBRARIES})
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
        endif()

        add_executable(numpy_exe numpy.cpp)
        target_include_directories(numpy_exe PRIVATE ${PYTHON_INCLUDE_DIRS})
        target_link_libraries(numpy_exe Boost::numpy${PYTHON_COMPONENT_SUFFIX} ${PYTHON_LIBRARIES})
    endif()
ENDIF()

ADD_EXECUTABLE(lambda_exe lambda.cpp)
# FIXME: The target Boost::boost cannot be created using current conan...
if (CONAN_BOOST_FINDPACKAGE)
    target_link_libraries(lambda_exe Boost::headers)
else()
    target_link_libraries(lambda_exe Boost::boost)
endif()
