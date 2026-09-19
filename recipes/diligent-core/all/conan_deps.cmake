find_package(SPIRV-headers REQUIRED CONFIG)
find_package(SPIRV-Tools REQUIRED CONFIG)
find_package(spirv-cross REQUIRED CONFIG)
find_package(volk REQUIRED CONFIG)
find_package(xxHash REQUIRED CONFIG)

if (NOT DILIGENT_NO_GLSLANG)
    find_package(glslang REQUIRED CONFIG)

    add_library(glslang INTERFACE)

    target_link_libraries(glslang INTERFACE
        glslang::glslang
    )

    target_include_directories(glslang INTERFACE
        ${glslang_INCLUDE_DIR}/glslang
    )

    add_library(SPIRV ALIAS glslang::SPIRV)
endif()

add_library(SPIRV-Headers ALIAS SPIRV-Headers::SPIRV-Headers)
add_library(spirv-tools-core ALIAS spirv-tools::spirv-tools)
# Conan's SPIRV-Tools package contains the source tree under res/.
# Diligent ShaderTools includes private SPIRV-Tools headers such as
# <source/opt/pass.h>.
function(conan_patch_diligent_shadertools)
    if(TARGET Diligent-ShaderTools)
        target_include_directories(Diligent-ShaderTools
            PRIVATE
                ${CONAN_SPIRV_TOOLS_SOURCE_DIR}
                ${CONAN_SPIRV_TOOLS_INCLUDE_DIR}
                ${CONAN_SPIRV_TOOLS_BUILD_DIR}
                ${CONAN_SPIRV_HEADERS_INCLUDE_DIR}
                ${CONAN_SPIRV_HEADERS_UNIFIED_INCLUDE_DIR}
        )

        message(STATUS
            "Conan: SPIRV-Tools source: ${CONAN_SPIRV_TOOLS_SOURCE_DIR}"
        )
        message(STATUS
            "Conan: SPIRV-Tools include: ${CONAN_SPIRV_TOOLS_INCLUDE_DIR}"
        )
    endif()
endfunction()

cmake_language(DEFER CALL conan_patch_diligent_shadertools)
