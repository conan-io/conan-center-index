cmake_minimum_required(VERSION 3.1)
project(FreeImage C CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(FREEIMAGE_FOLDER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

find_package(ZLIB REQUIRED)
find_package(PNG REQUIRED)
find_package(JPEG REQUIRED)
find_package(OpenJPEG REQUIRED)
find_package(libwebp REQUIRED)
find_package(JXR REQUIRED)
find_package(libraw REQUIRED)
find_package(OpenEXR REQUIRED)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# FreeImage

file(GLOB FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/*.cpp ${FREEIMAGE_FOLDER}/Source/FreeImage/*.c)
list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginG3.cpp)
list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginTIFF.cpp)
if(MSVC)
    list(APPEND FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/FreeImage.rc)
endif(MSVC)

file(GLOB FREEIMAGETOOLKIT_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/*.cpp ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/*.c)
list(REMOVE_ITEM FREEIMAGETOOLKIT_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/JPEGTransform.cpp)

file(GLOB METADATA_SOURCES ${FREEIMAGE_FOLDER}/Source/Metadata/*.cpp ${FREEIMAGE_FOLDER}/Source/Metadata/*.c)
list(REMOVE_ITEM METADATA_SOURCES ${FREEIMAGE_FOLDER}/Source/Metadata/XTIFF.cpp)

add_library(FreeImage ${FREEIMAGE_SOURCES} ${FREEIMAGETOOLKIT_SOURCES} ${METADATA_SOURCES})
set_target_properties(FreeImage PROPERTIES OUTPUT_NAME "freeimage")
target_include_directories(FreeImage PRIVATE
    ${FREEIMAGE_FOLDER}/Source
    ${FREEIMAGE_FOLDER}/Source/FreeImage
    ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit
    ${FREEIMAGE_FOLDER}/Source/Metadata
)
target_link_libraries(FreeImage PRIVATE
    ZLIB::ZLIB
    JPEG::JPEG
    OpenJPEG::OpenJPEG
    PNG::PNG
    libwebp::libwebp
    OpenEXR::OpenEXR
    libraw::libraw
    JXR::JXR
)
if(BUILD_SHARED_LIBS)
	target_compile_definitions(FreeImage PUBLIC FREEIMAGE_EXPORTS)
else()
	target_compile_definitions(FreeImage PUBLIC FREEIMAGE_LIB)
endif()

install(TARGETS FreeImage
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
set(FREEIMAGE_HEADERS ${FREEIMAGE_FOLDER}/Source/FreeImage.h)
install(FILES ${FREEIMAGE_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# FreeImagePlus

set(FREEIMAGEPLUS_HEADERS ${FREEIMAGE_FOLDER}/Wrapper/FreeImagePlus/FreeImagePlus.h)
file(GLOB FREEIMAGEPLUS_SOURCES ${FREEIMAGE_FOLDER}/Wrapper/FreeImagePlus/src/*.cpp ${FREEIMAGE_FOLDER}/Wrapper/FreeImagePlus/src/*.c)
if(MSVC)
    list(APPEND FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Wrapper/FreeImagePlus/FreeImagePlus.rc)
endif(MSVC)
add_library(FreeImagePlus ${FREEIMAGEPLUS_SOURCES} ${FREEIMAGEPLUS_HEADERS})
set_target_properties(FreeImagePlus PROPERTIES OUTPUT_NAME "freeimageplus")
target_link_libraries(FreeImagePlus PUBLIC FreeImage)
target_include_directories(FreeImagePlus PRIVATE
    ${FREEIMAGE_FOLDER}/Wrapper/FreeImagePlus
    ${FREEIMAGE_FOLDER}/Source
)
if(BUILD_SHARED_LIBS)
    target_compile_definitions(FreeImagePlus PRIVATE FIP_EXPORTS)
endif()

install(TARGETS FreeImagePlus
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${FREEIMAGEPLUS_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
