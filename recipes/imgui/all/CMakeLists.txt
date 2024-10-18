cmake_minimum_required(VERSION 3.15)
project(imgui LANGUAGES CXX)

if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()

add_library(imgui
    imgui.cpp
    imgui_demo.cpp
    imgui_draw.cpp
    imgui_tables.cpp
    imgui_widgets.cpp
    misc/cpp/imgui_stdlib.cpp
)
target_include_directories(imgui PUBLIC ${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR})

set_target_properties(imgui PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    OBJCXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)
set(IMGUI_EXPORT_HEADER imgui_export.h)
include(GenerateExportHeader)
generate_export_header(imgui
    EXPORT_MACRO_NAME IMGUI_API
    EXPORT_FILE_NAME ${IMGUI_EXPORT_HEADER}
)
# Enable __declspec(dllexport) in backend libs as well
add_compile_definitions(imgui_EXPORTS)

if(IMGUI_FREETYPE)
    find_package(freetype CONFIG REQUIRED)
    target_sources(imgui PRIVATE misc/freetype/imgui_freetype.cpp)
    target_link_libraries(imgui PRIVATE freetype)
    install(FILES misc/freetype/imgui_freetype.h DESTINATION include)
    if(IMGUI_FREETYPE_LUNASVG)
        find_package(lunasvg CONFIG REQUIRED)
        target_link_libraries(imgui PRIVATE lunasvg::lunasvg)
    endif()
endif()

if(IMGUI_ENABLE_OSX_DEFAULT_CLIPBOARD_FUNCTIONS)
    target_link_libraries(imgui PRIVATE "-framework ApplicationServices")
endif()

if(IMGUI_IMPL_ALLEGRO5)
    find_package(Allegro CONFIG REQUIRED)
    add_library(imgui-allegro5 backends/imgui_impl_allegro5.cpp)
    target_link_libraries(imgui-allegro5 PRIVATE Allegro::allegro Allegro::allegro_ttf Allegro::allegro_font Allegro::allegro_main)
    install(FILES backends/imgui_impl_allegro5.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-allegro5)
endif()

if(IMGUI_IMPL_ANDROID)
    add_library(imgui-android backends/imgui_impl_android.cpp)
    install(FILES backends/imgui_impl_android.h DESTINATION include)
    target_link_libraries(imgui-android PRIVATE android log EGL GLESv3)
    list(APPEND IMGUI_COMPONENTS imgui-android)
endif()

if(IMGUI_IMPL_DX9)
    add_library(imgui-dx9 backends/imgui_impl_dx9.cpp)
    target_link_libraries(imgui-dx9 PRIVATE d3d9)
    install(FILES backends/imgui_impl_dx9.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-dx9)
endif()

if(IMGUI_IMPL_DX10)
    add_library(imgui-dx10 backends/imgui_impl_dx10.cpp)
    target_link_libraries(imgui-dx9 PRIVATE d3d10)
    install(FILES backends/imgui_impl_dx10.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-dx10)
endif()

if(IMGUI_IMPL_DX11)
    add_library(imgui-dx11 backends/imgui_impl_dx11.cpp)
    target_link_libraries(imgui-dx11 PRIVATE d3d11)
    install(FILES backends/imgui_impl_dx11.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-dx11)
endif()

if(IMGUI_IMPL_DX12)
    add_library(imgui-dx12 backends/imgui_impl_dx12.cpp)
    target_link_libraries(imgui-dx12 PRIVATE d3d12)
    install(FILES backends/imgui_impl_dx12.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-dx12)
endif()

if(IMGUI_IMPL_GLFW)
    add_library(imgui-glfw backends/imgui_impl_glfw.cpp)
    if(NOT EMSCRIPTEN)
        find_package(glfw3 CONFIG REQUIRED)
        target_link_libraries(imgui-glfw PRIVATE glfw)
    endif()
    install(FILES backends/imgui_impl_glfw.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-glfw)
endif()

if(IMGUI_IMPL_GLUT)
    add_library(imgui-glut backends/imgui_impl_glut.cpp)
    if(NOT EMSCRIPTEN)
        find_package(GLUT REQUIRED)
        target_link_libraries(imgui-glut PRIVATE GLUT::GLUT)
    endif()
    install(FILES backends/imgui_impl_glut.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-glut)
endif()

if(IMGUI_IMPL_METAL)
    enable_language(OBJCXX)
    add_library(imgui-metal backends/imgui_impl_metal.mm)
    set_source_files_properties(backends/imgui_impl_metal.mm PROPERTIES COMPILE_FLAGS -fobjc-weak)
    target_link_libraries(imgui-metal PRIVATE
        "-framework Foundation"
        "-framework Metal"
        "-framework QuartzCore"
    )
    install(FILES backends/imgui_impl_metal.h DESTINATION include)
    if(IMGUI_IMPL_METAL_CPP)
        find_package(metal-cpp CONFIG REQUIRED)
        target_link_libraries(imgui-metal PRIVATE metal-cpp::metal-cpp)
    endif()
    list(APPEND IMGUI_COMPONENTS imgui-metal)
endif()

if(IMGUI_IMPL_OPENGL2)
    find_package(OpenGL REQUIRED)
    add_library(imgui-opengl2 backends/imgui_impl_opengl2.cpp)
    target_link_libraries(imgui-opengl2 PRIVATE OpenGL::GL)
    install(FILES backends/imgui_impl_opengl2.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-opengl2)
endif()

if(IMGUI_IMPL_OPENGL3)
    find_package(OpenGL REQUIRED)
    add_library(imgui-opengl3 backends/imgui_impl_opengl3.cpp)
    target_link_libraries(imgui-opengl3 PRIVATE OpenGL::GL)
    install(FILES backends/imgui_impl_opengl3.h DESTINATION include)
    install(FILES backends/imgui_impl_opengl3_loader.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-opengl3)
endif()

if(IMGUI_IMPL_OSX)
    enable_language(OBJCXX)
    add_library(imgui-osx backends/imgui_impl_osx.mm)
    target_link_libraries(imgui-osx PRIVATE
        "-framework AppKit"
        "-framework Carbon"
        "-framework Cocoa"
        "-framework Foundation"
        "-framework GameController"
    )
    install(FILES backends/imgui_impl_osx.h DESTINATION include)
    if(IMGUI_IMPL_METAL_CPP_EXTENSIONS)
        find_package(metal-cpp CONFIG REQUIRED)
        target_link_libraries(imgui-osx PRIVATE metal-cpp::metal-cpp)
    endif()
    list(APPEND IMGUI_COMPONENTS imgui-osx)
endif()

if(IMGUI_IMPL_SDL2)
    find_package(SDL2 CONFIG REQUIRED)
    add_library(imgui-sdl2 backends/imgui_impl_sdl2.cpp)
    target_link_libraries(imgui-sdl2 PRIVATE SDL2::SDL2)
    install(FILES backends/imgui_impl_sdl2.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-sdl2)
endif()

if(IMGUI_IMPL_SDLRENDERER2)
    find_package(SDL2 CONFIG REQUIRED)
    add_library(imgui-sdlrenderer2 backends/imgui_impl_sdlrenderer2.cpp)
    target_link_libraries(imgui-sdlrenderer2 PRIVATE SDL2::SDL2)
    install(FILES backends/imgui_impl_sdlrenderer2.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-sdlrenderer2)
endif()

if(IMGUI_IMPL_VULKAN)
    find_package(Vulkan REQUIRED)
    add_library(imgui-vulkan backends/imgui_impl_vulkan.cpp)
    target_link_libraries(imgui-vulkan PRIVATE Vulkan::Vulkan)
    install(FILES backends/imgui_impl_vulkan.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-vulkan)
endif()

if(IMGUI_IMPL_WIN32)
    add_library(imgui-win32 backends/imgui_impl_win32.cpp)
    target_link_libraries(imgui-win32 PRIVATE dwmapi xinput)
    install(FILES backends/imgui_impl_win32.h DESTINATION include)
    list(APPEND IMGUI_COMPONENTS imgui-win32)
endif()

foreach(component ${IMGUI_COMPONENTS})
    target_link_libraries(${component} PUBLIC imgui)
endforeach()

if(IMGUI_IMPL_TOOLS)
    add_executable(binary_to_compressed_c misc/fonts/binary_to_compressed_c.cpp)
    install(TARGETS binary_to_compressed_c DESTINATION bin)
endif()

install(TARGETS imgui ${IMGUI_COMPONENTS}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

file(GLOB IMGUI_HEADERS *.h)
install(FILES
        misc/cpp/imgui_stdlib.h
        ${IMGUI_HEADERS}
        ${PROJECT_BINARY_DIR}/${IMGUI_EXPORT_HEADER}
    DESTINATION include
)

file(GLOB EXTRA_FONTS_FILES misc/fonts/*.ttf)
install(FILES ${EXTRA_FONTS_FILES} DESTINATION res/fonts)

if (MSVC)
    file(GLOB EXTRA_NATVIS_FILES misc/natvis/*.natvis)
    install(FILES ${EXTRA_NATVIS_FILES} DESTINATION res/natvis)
endif()
