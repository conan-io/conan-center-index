find_package(SPIRV-Headers REQUIRED CONFIG)
find_package(SPIRV-Tools REQUIRED CONFIG)
find_package(spirv-cross REQUIRED CONFIG)
find_package(volk REQUIRED CONFIG)
find_package(xxHash REQUIRED CONFIG)
find_package(GLEW REQUIRED CONFIG)

if(NOT DILIGENT_NO_GLSLANG)
    find_package(glslang REQUIRED CONFIG)
    add_library(glslang INTERFACE)
    target_link_libraries(glslang INTERFACE glslang::glslang)
    target_include_directories(glslang INTERFACE ${glslang_INCLUDE_DIR}/glslang)
    add_library(SPIRV ALIAS glslang::SPIRV)
endif()

if(LINUX)
    # X11/XCB is not acutally linked against or included anywhere
    find_package(X11 REQUIRED)
    link_libraries(X11::X11)
endif()

add_library(SPIRV-Headers ALIAS SPIRV-Headers::SPIRV-Headers)
add_library(spirv-tools-core ALIAS spirv-tools::spirv-tools)
