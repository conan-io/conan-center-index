cmake_minimum_required(VERSION 3.12)
project(SDL2_image LANGUAGES C)

find_package(SDL2 REQUIRED CONFIG)

macro(add_image_option type)
    option(SDL2IMAGE_${type} "${type} images support" ON)
    if(SDL2IMAGE_${type})
        add_definitions("-DLOAD_${type}")
        if(SDL2IMAGE_${type}_SHARED)
            add_definitions("-DLOAD_${type}_DYNAMIC")
        endif()
    endif()
endmacro()

if(APPLE)
    option(SDL2IMAGE_BACKEND_IMAGEIO "use native Apple frameworks for loading images" ON)
    if(SDL2IMAGE_BACKEND_IMAGEIO)
        set(IMAGEIO_SOURCE "${SDL_IMAGE_SRC_DIR}/IMG_ImageIO.m")
    else()
        add_definitions("-DSDL_IMAGE_USE_COMMON_BACKEND")
    endif()
endif()

add_image_option(BMP)
add_image_option(GIF)
add_image_option(JPG)
add_image_option(LBM)
add_image_option(PCX)
add_image_option(PNG)
add_image_option(PNM)
add_image_option(SVG)
add_image_option(TGA)
add_image_option(TIF)
add_image_option(WEBP)
add_image_option(XCF)
add_image_option(XPM)
add_image_option(XV)

set(SOURCES
    ${SDL_IMAGE_SRC_DIR}/IMG.c
    ${SDL_IMAGE_SRC_DIR}/IMG_bmp.c
    ${SDL_IMAGE_SRC_DIR}/IMG_gif.c
    ${SDL_IMAGE_SRC_DIR}/IMG_jpg.c
    ${SDL_IMAGE_SRC_DIR}/IMG_lbm.c
    ${SDL_IMAGE_SRC_DIR}/IMG_pcx.c
    ${SDL_IMAGE_SRC_DIR}/IMG_png.c
    ${SDL_IMAGE_SRC_DIR}/IMG_pnm.c
    ${SDL_IMAGE_SRC_DIR}/IMG_svg.c
    ${SDL_IMAGE_SRC_DIR}/IMG_tga.c
    ${SDL_IMAGE_SRC_DIR}/IMG_tif.c
    ${SDL_IMAGE_SRC_DIR}/IMG_webp.c
    ${SDL_IMAGE_SRC_DIR}/IMG_xcf.c
    ${SDL_IMAGE_SRC_DIR}/IMG_xpm.c
    ${SDL_IMAGE_SRC_DIR}/IMG_xv.c
    ${IMAGEIO_SOURCE}
)

if(BUILD_SHARED_LIBS)
    list(APPEND SOURCES ${SDL_IMAGE_SRC_DIR}/version.rc)
endif()

add_library(${PROJECT_NAME} ${SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${SDL_IMAGE_SRC_DIR})
set_target_properties(${PROJECT_NAME} PROPERTIES
    PUBLIC_HEADER ${SDL_IMAGE_SRC_DIR}/SDL_image.h
    DEFINE_SYMBOL DLL_EXPORT
)

if(SDL_IS_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE SDL2::SDL2-static)
endif()

if(SDL2IMAGE_TIF AND NOT SDL2IMAGE_TIF_SHARED)
    find_package(TIFF REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE TIFF::TIFF)
endif()

if(SDL2IMAGE_JPG AND NOT SDL2IMAGE_JPEG_SHARED)
    find_package(JPEG REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
endif()

if(SDL2IMAGE_PNG AND NOT SDL2IMAGE_PNG_SHARED)
    find_package(PNG REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE PNG::PNG)
endif()

if(SDL2IMAGE_WEBP AND NOT SDL2IMAGE_WEBP_SHARED)
    find_package(WebP REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE WebP::webp)
endif()

if(APPLE AND SDL2IMAGE_BACKEND_IMAGEIO AND BUILD_SHARED_LIBS)
    if(${CMAKE_SYSTEM_NAME} STREQUAL Darwin)
        set(extraFrameworks
            "-framework ApplicationServices"
        )
    else()
        set(extraFrameworks
            "-framework MobileCoreServices"
            "-framework UIKit"
        )
    endif()
    target_link_libraries(${PROJECT_NAME} PRIVATE
        "-framework CoreFoundation"
        "-framework CoreGraphics"
        "-framework Foundation"
        "-framework ImageIO"
        ${extraFrameworks}
    )
endif()

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/SDL2"
)
