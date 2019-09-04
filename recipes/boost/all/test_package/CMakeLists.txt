PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)
enable_testing()

set(Boost_DEBUG 1)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

CONAN_BASIC_SETUP()

IF(NOT HEADER_ONLY)
	if(WITH_PYTHON)
		find_package(Boost COMPONENTS regex python REQUIRED)
	else()
		find_package(Boost COMPONENTS regex REQUIRED)
	endif()

    include_directories(${Boost_INCLUDE_DIRS})
    ADD_EXECUTABLE(lambda lambda.cpp)
    ADD_EXECUTABLE(regex_exe regex.cpp)
    ADD_EXECUTABLE(test test.cpp)
    TARGET_LINK_LIBRARIES(regex_exe ${Boost_LIBRARIES})
    MESSAGE("LIBS=> ${CONAN_LIBS}")
    TARGET_LINK_LIBRARIES(test ${CONAN_LIBS})
    if(WITH_PYTHON)
        add_library(hello_ext SHARED python.cpp)
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
            target_include_directories(hello_ext PRIVATE C:/Python27/include)
            target_link_libraries(hello_ext C:/Python27/libs/python27.lib ${CONAN_LIBS})
        endif()
    endif()
    ADD_TEST(NAME TestRegex
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")

ELSE()
	ADD_EXECUTABLE(lambda lambda.cpp)
ENDIF()

ADD_TEST(NAME TestLambda
         COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda>" ${TEST_ARGS})

IF(NOT HEADER_ONLY)
    # Test a different exe linking with the CONAN_LIBS to actually test the package_info
    ADD_EXECUTABLE(newregex regex.cpp)
    TARGET_LINK_LIBRARIES(newregex ${CONAN_LIBS})
    ADD_TEST(NAME TestRegexNew
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:newregex>" ${TEST_ARGS})
ENDIF()
