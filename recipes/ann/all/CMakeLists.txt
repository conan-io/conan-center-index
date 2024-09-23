cmake_minimum_required(VERSION 3.15)
project(ANN LANGUAGES CXX)

include(GNUInstallDirs)

file(GLOB ANN_SRC_FILES ${ANN_SRC_DIR}/src/*.cpp)

add_library(ANN ${ANN_SRC_FILES})
target_include_directories(ANN PUBLIC ${ANN_SRC_DIR}/include)

if(WIN32)
    if(BUILD_SHARED_LIBS)
        set_target_properties(ANN PROPERTIES
            CXX_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN TRUE
        )
        target_compile_definitions(ANN PRIVATE DLL_EXPORTS)
    else()
        target_compile_definitions(ANN PUBLIC ANN_STATIC)
    endif()
endif()

install(DIRECTORY ${ANN_SRC_DIR}/include/ANN DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(
    TARGETS ANN
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
