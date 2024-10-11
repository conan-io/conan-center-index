cmake_minimum_required(VERSION 3.8)
project(LibRaw LANGUAGES CXX)

option(LIBRAW_BUILD_THREAD_SAFE "Build raw_r library with -pthread enabled" OFF)
option(LIBRAW_WITH_JPEG "Build with libjpeg" ON)
option(LIBRAW_WITH_LCMS "Build with LCMS" ON)
option(LIBRAW_WITH_JASPER "Build with Jasper" ON)

if(RAW_LIB_VERSION_STRING VERSION_LESS 0.21)
    set(libraw_LIB_SRCS ${LIBRAW_SRC_DIR}/internal/dcraw_common.cpp
                        ${LIBRAW_SRC_DIR}/internal/dcraw_fileio.cpp
                        ${LIBRAW_SRC_DIR}/internal/demosaic_packs.cpp
                        ${LIBRAW_SRC_DIR}/src/libraw_cxx.cpp
                        ${LIBRAW_SRC_DIR}/src/libraw_c_api.cpp
                        ${LIBRAW_SRC_DIR}/src/libraw_datastream.cpp
    )
else()
    file(GLOB_RECURSE libraw_LIB_SRCS CONFIGURE_DEPENDS "${LIBRAW_SRC_DIR}/src/*.cpp")

    # Exclude placeholder (stub) implementations
    file(GLOB_RECURSE exclude_libraw_LIB_SRCS CONFIGURE_DEPENDS "${LIBRAW_SRC_DIR}/src/*_ph.cpp")
    list(REMOVE_ITEM libraw_LIB_SRCS ${exclude_libraw_LIB_SRCS})
endif()

if(LIBRAW_WITH_JPEG)
    find_package(JPEG REQUIRED)
endif()
if(LIBRAW_WITH_LCMS)
    find_package(lcms REQUIRED CONFIG)
endif()
if(LIBRAW_WITH_JASPER)
    find_package(Jasper REQUIRED)
endif()

add_library(raw ${libraw_LIB_SRCS})
target_compile_features(raw PUBLIC cxx_std_11)
target_include_directories(raw PUBLIC "${LIBRAW_SRC_DIR}")
if(WIN32)
    target_link_libraries(raw PUBLIC ws2_32)
    if(BUILD_SHARED_LIBS)
        target_compile_definitions(raw PUBLIC LIBRAW_BUILDLIB)
    else()
        target_compile_definitions(raw PUBLIC LIBRAW_NODLL)
    endif()
endif()
if(MSVC)
    target_compile_options(raw PUBLIC /wd4018 /wd4101 /wd4244 /wd4251 /wd4267 /wd4996)
endif()
if(LIBRAW_WITH_JPEG)
    target_compile_definitions(raw PUBLIC USE_JPEG USE_JPEG8)
    target_link_libraries(raw PUBLIC JPEG::JPEG)
endif ()
if (LIBRAW_WITH_LCMS)
    target_compile_definitions(raw PUBLIC USE_LCMS2)
    target_link_libraries(raw PUBLIC lcms::lcms)
endif ()
if (LIBRAW_WITH_JASPER)
    target_compile_definitions(raw PUBLIC USE_JASPER)
    target_link_libraries(raw PUBLIC Jasper::Jasper)
endif ()

include(GNUInstallDirs)
if(LIBRAW_BUILD_THREAD_SAFE)
    add_library(raw_r ${libraw_LIB_SRCS})
    target_link_libraries(raw_r INTERFACE raw)
    target_compile_options(raw_r PRIVATE -pthread)
    target_link_options(raw_r PRIVATE -pthread)
    target_include_directories(raw_r PUBLIC "${LIBRAW_SRC_DIR}")
    install(
        TARGETS raw_r
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
endif()

install(DIRECTORY "${LIBRAW_SRC_DIR}/libraw" DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(
    TARGETS raw
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
