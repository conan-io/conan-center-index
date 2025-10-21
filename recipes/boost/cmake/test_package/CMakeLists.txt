cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

if(UNIX AND NOT APPLE AND NOT EMSCRIPTEN)
    # use RPATH instead of RUNPATH so that
    # transitive dependencies can be located
    add_link_options("LINKER:--disable-new-dtags")
endif()

include(CTest)
enable_testing()

    if(WITH_RANDOM)
        find_package(Boost COMPONENTS random REQUIRED)
        add_executable(random_exe random.cpp)
        target_link_libraries(random_exe PRIVATE Boost::random)
        add_test(NAME boost_random COMMAND random_exe)
    endif()

    if(WITH_CHRONO)
        find_package(Boost COMPONENTS chrono REQUIRED)
        add_executable(chrono_exe chrono.cpp)
        target_link_libraries(chrono_exe PRIVATE Boost::chrono)
        set_property(TARGET chrono_exe PROPERTY CXX_STANDARD 11)
        add_test(NAME chrono_test COMMAND chrono_exe)
    endif()

    if(WITH_JSON)
        find_package(Boost COMPONENTS json REQUIRED)
        add_executable(json_exe json.cpp)
        target_link_libraries(json_exe PRIVATE Boost::json)
        set_property(TARGET json_exe PROPERTY CXX_STANDARD 11)
        add_test(NAME boost_json COMMAND json_exe)
    endif()

    if(WITH_LOCALE)
        find_package(Boost COMPONENTS locale REQUIRED)
        add_executable(locale_exe locale.cpp)
        target_link_libraries(locale_exe PRIVATE Boost::locale)
        set_property(TARGET locale_exe PROPERTY CXX_STANDARD 11)
        add_test(NAME boost_locale COMMAND locale_exe)
    endif()

    if(WITH_URL)
        find_package(Boost COMPONENTS url REQUIRED)
        add_executable(url_exe url.cpp)
        target_link_libraries(url_exe PRIVATE Boost::url)
        set_property(TARGET url_exe PROPERTY CXX_STANDARD 11)
        add_test(NAME boost_url COMMAND url_exe)

endif()
