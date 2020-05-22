cmake_minimum_required(VERSION 2.8)
project(test_package)
enable_testing()

set(Boost_DEBUG 1)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

CONAN_BASIC_SETUP()

macro( target_link_to_icu target )

    if(NOT ICU_FOUND)
        set(ICU_DEBUG 1)
        set(ICU_ROOT "${CONAN_ICU_ROOT}")
        find_package(ICU COMPONENTS i18n uc data REQUIRED)
    endif()

    target_include_directories( ${target} PUBLIC ${ICU_INCLUDE_DIRS} )

    if( ( NOT ICU_USE_STATIC_LIBS )
	          OR Boost_USE_STATIC_LIBS
	          OR APPLE )
        target_link_libraries( ${target} PUBLIC ${ICU_LIBRARIES} )
    endif()

    if(MSVC)
        target_link_libraries( ${target} PUBLIC advapi32 )
    elseif(UNIX AND NOT APPLE )
        target_link_libraries( ${target} PUBLIC dl )
    endif()

endmacro()



IF(NOT HEADER_ONLY)
    set(boost_components)
    if (WITH_COROUTINE)
        list(APPEND boost_components coroutine)
        list(APPEND boost_components thread)
    endif()
    if (WITH_LOCALE)
        list(APPEND boost_components locale)
        if( USE_ICU )
            list( APPEND boost_components thread )
        endif()
    endif()
    if (WITH_PYTHON)
        list(APPEND boost_components python)
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
        TARGET_LINK_LIBRARIES(random_exe ${Boost_LIBRARIES})
    endif()
    if (WITH_REGEX)
        ADD_EXECUTABLE(regex_exe regex.cpp)
        TARGET_LINK_LIBRARIES(regex_exe ${Boost_LIBRARIES})
        if( USE_ICU )
            target_link_to_icu( regex_exe )
            target_compile_definitions( regex_exe PUBLIC USE_ICU )
        endif()

    endif()

    if (WITH_TEST)
        ADD_EXECUTABLE(test_exe test.cpp)
        TARGET_LINK_LIBRARIES(test_exe ${CONAN_LIBS})
    endif()

    if (WITH_COROUTINE)
        ADD_EXECUTABLE(coroutine_exe coroutine.cpp)
        TARGET_LINK_LIBRARIES(coroutine_exe ${Boost_LIBRARIES})
    endif()

    if (WITH_CHRONO)
        ADD_EXECUTABLE(chrono_exe chrono.cpp)
        TARGET_LINK_LIBRARIES(chrono_exe ${CONAN_LIBS})
    endif()

    if( WITH_LOCALE )
        add_executable(locale_exe locale.cpp)
        target_link_libraries(locale_exe ${Boost_LIBRARIES} )
        if( USE_ICU )
            target_link_to_icu( locale_exe )
            target_compile_definitions( locale_exe PUBLIC USE_ICU )
        endif()
        if( USE_ICONV )
            find_package( Iconv REQUIRED )
            if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                target_link_libraries( locale_exe ${Iconv_LIBRARIES} )
            endif()
        endif()
        add_test(NAME TestLocale
            COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:locale_exe>")
        if(UNIX)
            find_package( Iconv REQUIRED )
            if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                target_link_libraries( locale_exe ${Iconv_LIBRARIES} )
            endif()
        endif()
    endif()

    if(WITH_PYTHON)
        add_library(hello_ext SHARED python.cpp)
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
            target_include_directories(hello_ext PRIVATE C:/Python27/include)
            target_link_libraries(hello_ext C:/Python27/libs/python27.lib ${CONAN_LIBS})
        endif()
    endif()

    if (WITH_REGEX)
        ADD_TEST(NAME TestRegex
                 COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")
    endif()
ENDIF()

ADD_EXECUTABLE(lambda_exe lambda.cpp)

ADD_TEST(NAME TestLambda
         COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda_exe>" ${TEST_ARGS})

IF(NOT HEADER_ONLY AND WITH_REGEX)
    # Test a different exe linking with the CONAN_LIBS to actually test the package_info
    ADD_EXECUTABLE(newregex regex.cpp)
    TARGET_LINK_LIBRARIES(newregex ${CONAN_LIBS})
    ADD_TEST(NAME TestRegexNew
             COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:newregex>" ${TEST_ARGS})
ENDIF()
