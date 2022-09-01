cmake_minimum_required(VERSION 3.1)
project(SDL2_image LANGUAGES C)

find_package(SDL2 REQUIRED CONFIG)

macro(add_image_option type)
    option(${type} "${type} images support" ON)
    if(${type})
        add_definitions("-DLOAD_${type}")
        if(${type}_DYNAMIC)
            add_definitions("-DLOAD_${type}_DYNAMIC")
        endif()
    endif()
endmacro()

if(APPLE)
    option(IMAGEIO "use native Mac OS X frameworks for loading images" ON)
    if(IMAGEIO)
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

if(TIF)
    find_package(TIFF REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE TIFF::TIFF)
endif()

if(JPG)
    find_package(JPEG REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
endif()

if(PNG)
    find_package(PNG REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE PNG::PNG)
endif()

if(WEBP)
    find_package(WebP REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE WebP::webp)
endif()

install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "lib"
    LIBRARY DESTINATION "lib"
    RUNTIME DESTINATION "bin"
    PUBLIC_HEADER DESTINATION "include/SDL2"
)
