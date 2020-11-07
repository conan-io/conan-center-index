cmake_minimum_required(VERSION 3.13)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32)
    add_definitions (-D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING)
    add_definitions (-D_WIN32_WINNT=_WIN32_WINNT_WIN8)
endif()

add_subdirectory("source_subfolder")

target_link_libraries(cppcommon PRIVATE ${CONAN_LIBS})

target_compile_features(cppcommon PUBLIC cxx_std_17)

install(DIRECTORY source_subfolder/include/
        DESTINATION include
        FILES_MATCHING
        PATTERN "*.h"
        PATTERN "*.inl")

install(DIRECTORY source_subfolder/plugins/
        DESTINATION include/plugins
        FILES_MATCHING
        PATTERN "*.h")

if(UNIX AND NOT APPLE)
    target_link_libraries(cppcommon PUBLIC dl rt)
endif()

if(WIN32)
    target_link_libraries(cppcommon PUBLIC rpcrt4 userenv)
    if(BUILD_SHARED_LIBS)
        set_target_properties(cppcommon PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    endif()
endif()
