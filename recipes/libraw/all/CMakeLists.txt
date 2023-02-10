cmake_minimum_required(VERSION 3.8)
project(LibRaw LANGUAGES CXX)

file(GLOB_RECURSE headers "${LIBRAW_SRC_DIR}/libraw/*.h")


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

if(WIN32)
    add_definitions(-DWIN32)

    if(BUILD_SHARED_LIBS)
        add_definitions(-DLIBRAW_BUILDLIB)
    else()
        add_definitions(-DLIBRAW_NODLL)
    endif()
endif()

find_package(JPEG CONFIG)
find_package(libjpeg-turbo CONFIG)
find_package(lcms CONFIG)
find_package(Jasper CONFIG)

if (TARGET JPEG::JPEG OR TARGET libjpeg-turbo::jpeg OR TARGET libjpeg-turbo::jpeg_static)
    add_definitions(-DUSE_JPEG -DUSE_JPEG8)
endif ()
if (TARGET lcms::lcms)
    add_definitions(-DUSE_LCMS2)
endif ()
if (TARGET Jasper::Jasper)
    add_definitions(-DUSE_JASPER)
endif ()

add_library(raw ${headers} ${libraw_LIB_SRCS})
target_compile_features(raw PRIVATE cxx_std_11)
target_include_directories(raw PUBLIC "${LIBRAW_SRC_DIR}")
set_target_properties(raw PROPERTIES LINKER_LANGUAGE CXX)
target_compile_options(raw PUBLIC $<$<CXX_COMPILER_ID:MSVC>:/W0>)
if (TARGET JPEG::JPEG)
    target_link_libraries(raw PUBLIC JPEG::JPEG)
endif ()
if (TARGET libjpeg-turbo::jpeg)
    target_link_libraries(raw PUBLIC libjpeg-turbo::jpeg)
endif ()
if (TARGET libjpeg-turbo::jpeg_static)
    target_link_libraries(raw PUBLIC libjpeg-turbo::jpeg_static)
endif ()
if (TARGET lcms::lcms)
    target_link_libraries(raw PUBLIC lcms::lcms)
endif ()
if (TARGET Jasper::Jasper)
    target_link_libraries(raw PUBLIC Jasper::Jasper)
endif ()

install(DIRECTORY "${LIBRAW_SRC_DIR}/libraw" DESTINATION include)
install(TARGETS raw ARCHIVE DESTINATION lib RUNTIME DESTINATION bin LIBRARY DESTINATION lib)
