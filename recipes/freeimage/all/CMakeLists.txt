cmake_minimum_required(VERSION 3.1)
project(FreeImage C CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(FREEIMAGE_FOLDER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

find_package(ZLIB REQUIRED)
if(WITH_PNG)
    find_package(PNG REQUIRED)
endif()
if(WITH_JPEG)
    find_package(JPEG REQUIRED)
endif()
if(WITH_OPENJPEG)
    find_package(OpenJPEG REQUIRED)
endif()
if(WITH_WEBP)
    find_package(WebP REQUIRED)
endif()
if(WITH_JXR)
    find_package(JXR REQUIRED)
endif()
if(WITH_RAW)
    find_package(libraw REQUIRED)
endif()
if(WITH_OPENEXR)
    find_package(OpenEXR REQUIRED)
endif()
if(WITH_TIFF)
    find_package(TIFF REQUIRED)
endif()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# FreeImage

file(GLOB FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/*.cpp ${FREEIMAGE_FOLDER}/Source/FreeImage/*.c)
list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginG3.cpp)
if(NOT WITH_PNG)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginPNG.cpp)
endif()
if(NOT WITH_JPEG)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginJPEG.cpp)
endif()
if(NOT WITH_OPENJPEG)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginJP2.cpp)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginJ2K.cpp)
endif()
if(NOT WITH_WEBP)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginWebP.cpp)
endif()
if(NOT WITH_JXR)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginJXR.cpp)
endif()
if(NOT WITH_RAW)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginRAW.cpp)
endif()
if(NOT WITH_OPENEXR)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginEXR.cpp)
endif()
if(NOT WITH_TIFF)
    list(REMOVE_ITEM FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImage/PluginTIFF.cpp)
endif()
if(MSVC)
    list(APPEND FREEIMAGE_SOURCES ${FREEIMAGE_FOLDER}/FreeImage.rc)
endif(MSVC)

file(GLOB FREEIMAGETOOLKIT_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/*.cpp ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/*.c)
list(REMOVE_ITEM FREEIMAGETOOLKIT_SOURCES ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit/JPEGTransform.cpp)

file(GLOB METADATA_SOURCES ${FREEIMAGE_FOLDER}/Source/Metadata/*.cpp ${FREEIMAGE_FOLDER}/Source/Metadata/*.c)
if(NOT WITH_TIFF)
   list(REMOVE_ITEM METADATA_SOURCES ${FREEIMAGE_FOLDER}/Source/Metadata/XTIFF.cpp)
endif()

add_library(FreeImage ${FREEIMAGE_SOURCES} ${FREEIMAGETOOLKIT_SOURCES} ${METADATA_SOURCES})
set_target_properties(FreeImage PROPERTIES OUTPUT_NAME "freeimage")
target_include_directories(FreeImage PRIVATE
    ${FREEIMAGE_FOLDER}/Source
    ${FREEIMAGE_FOLDER}/Source/FreeImage
    ${FREEIMAGE_FOLDER}/Source/FreeImageToolkit
    ${FREEIMAGE_FOLDER}/Source/Metadata
)
target_link_libraries(FreeImage PRIVATE ZLIB::ZLIB)
if(WITH_PNG)
    target_link_libraries(FreeImage PRIVATE PNG::PNG)
endif()
if(WITH_JPEG)
    target_link_libraries(FreeImage PRIVATE JPEG::JPEG)
endif()
if(WITH_OPENJPEG)
    target_link_libraries(FreeImage PRIVATE OpenJPEG::OpenJPEG)
endif()
if(WITH_WEBP)
    target_link_libraries(FreeImage PRIVATE WebP::WebP)
endif()
if(WITH_JXR)
    target_link_libraries(FreeImage PRIVATE JXR::JXR)
endif()
if(WITH_RAW)
    target_link_libraries(FreeImage PRIVATE libraw::libraw)
endif()
if(WITH_OPENEXR)
    target_link_libraries(FreeImage PRIVATE OpenEXR::OpenEXR)
endif()
if(WITH_TIFF)
    target_link_libraries(FreeImage PRIVATE TIFF::TIFF)
endif()
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
