from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.files import rm, get, rmdir, collect_libs, export_conandata_patches, copy, apply_conandata_patches
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=2.1"


class DiligentCoreConan(ConanFile):
    name = "diligent-core"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentCore"
    description = "Diligent Core is a modern cross-platfrom low-level graphics API."
    license = "Apache-2.0"
    topics = ("graphics", "opengl", "vulkan", "directx", "shaders", "openxr", "raytracing")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC":   [True, False],
        "with_glslang": [True, False],
    }
    default_options = {
        "shared": False	,
        "fPIC": True,
        "with_glslang": True
    }

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")
        # ThirdParty/CMakeLists.txt needs the spirv-cross-core target, and Archiver links spirv-cross-glsl
        if self.dependencies["spirv-cross"].options.shared or not self.dependencies["spirv-cross"].options.glsl:
            raise ConanInvalidConfiguration(f"{self.ref} requires a static spirv-cross with the glsl option enabled")

    def export_sources(self):
        copy(self, "conan_deps.cmake", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"), keep_path=False)
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Dependencies are provided by Conan. Dawn and abseil-cpp are only needed by the WebGPU backend, which is disabled
        for folder in ["abseil-cpp", "dawn", "glew", "glslang", "SPIRV-Cross", "SPIRV-Headers",
                       "SPIRV-Tools", "volk", "Vulkan-Headers", "xxHash"]:
            rmdir(self, os.path.join(self.source_folder, "ThirdParty", folder))
        apply_conandata_patches(self)

    def package_id(self):
        if is_msvc(self.info):
            if is_msvc_static_runtime(self.info):
                self.info.settings.compiler.runtime = "MT/MTd"
            else:
                self.info.settings.compiler.runtime = "MD/MDd"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DILIGENT_BUILD_SAMPLES"] = False
        tc.variables["DILIGENT_NO_FORMAT_VALIDATION"] = True
        tc.variables["DILIGENT_BUILD_TESTS"] = False
        tc.variables["DILIGENT_NO_DXC"] = True
        tc.variables["DILIGENT_NO_WEBGPU"] = True
        tc.variables["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        # DLSS and DirectSR headers are downloaded via cmake FetchContent
        tc.variables["DILIGENT_NO_DLSS"] = True
        tc.variables["DILIGENT_NO_DSR"] = True
        tc.variables["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.dependencies["spirv-cross"].options.namespace
        tc.variables["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        tc.variables["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_EXCEPTIONS"] = True
        tc.variables[self._diligent_platform()] = True
        tc.cache_variables["CMAKE_PROJECT_DiligentCore_INCLUDE"] = os.path.join(self.source_folder, "conan_deps.cmake")
        # By default, Diligent builds static and shared versions of every main library. We select the one we
        # want based on options.shared in package(). To avoid building every intermediate library as SHARED,
        # we have to disable BUILD_SHARED_LIBS.
        tc.cache_variables["BUILD_SHARED_LIBS"] = False
        # Disable installing NVAPI via FetchContent
        tc.cache_variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("glew", "cmake_target_name", "GLEW::glew")
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def requirements(self):
        self.requires("opengl/system")

        spirv_version = "1.4.357.0"
        self.requires(f"spirv-cross/{spirv_version}")
        self.requires(f"spirv-tools/{spirv_version}")
        if self.options.with_glslang:
            self.requires(f"glslang/{spirv_version}")
        self.requires(f"vulkan-headers/{spirv_version}")
        self.requires(f"vulkan-validationlayers/{spirv_version}")
        self.requires(f"volk/{spirv_version}")
        self.requires("xxhash/0.8.3")
        self.requires("glew/2.2.0")
        if self.settings.os == "Linux":
            self.requires("wayland/[>=1.22.0 <2]")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            if not cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.13.1")

    def _diligent_platform(self):
        if self.settings.os == "Windows":
            return "PLATFORM_WIN32"
        elif self.settings.os == "Macos":
            return "PLATFORM_MACOS"
        elif self.settings.os == "Linux":
            return "PLATFORM_LINUX"
        elif self.settings.os == "Android":
            return "PLATFORM_ANDROID"
        elif self.settings.os == "iOS":
            return "PLATFORM_IOS"
        elif self.settings.os == "Emscripten":
            return "PLATFORM_EMSCRIPTEN"
        elif self.settings.os == "watchOS":
            return "PLATFORM_TVOS"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "Licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.package_folder, self.source_folder))

        if self.options.shared:
            copy(self, pattern="*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
            rm(self, os.path.join(self.package_folder, "lib"), "*.a", recursive=True)
            if self.settings.os != "Windows":
                rm(self, os.path.join(self.package_folder, "lib"), "*.lib", recursive=True)
        else:
            copy(self, pattern="*.a",   dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            rm(self, os.path.join(self.package_folder, "lib"), "*.dylib", recursive=True)
            rm(self, os.path.join(self.package_folder, "lib"), "*.so", recursive=True)
            rm(self, os.path.join(self.package_folder, "lib"), "*.dll", recursive=True)

        copy(self, pattern="*.fxh", dst=os.path.join(self.package_folder, "res"), src=self.source_folder, keep_path=False)
        copy(self, "File2String*",  dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        # MinGw creates many invalid files, called objects.a, remove them here:
        rm(self, "objects.a", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        # included as discussed here https://github.com/conan-io/conan-center-index/pull/10732#issuecomment-1123596308
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include"))
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "Common"))

        self.cpp_info.includedirs.append(os.path.join("include"))
        self.cpp_info.includedirs.append(os.path.join("include", "Common", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsEngine", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsEngineVulkan", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsEngineOpenGL", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsAccessories", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsTools", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "HLSL2GLSLConverterLib", "interface"))
        archiver_path = os.path.join("include", "Graphics", "Archiver", "interface")
        if os.path.isdir(archiver_path):
            self.cpp_info.includedirs.append(archiver_path)

        self.cpp_info.includedirs.append(os.path.join("include", "Primitives", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Basic", "interface"))
        if self.settings.os == "Android":
            self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Android", "interface"))
        elif is_apple_os(self):
            self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Apple", "interface"))
        elif self.settings.os == "Emscripten":
            self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Emscripten", "interface"))
        elif self.settings.os == "Linux":
            self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Linux", "interface"))
        elif self.settings.os == "Windows":
            self.cpp_info.includedirs.append(os.path.join("include", "Platforms", "Win32", "interface"))
            self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsEngineD3D11", "interface"))
            self.cpp_info.includedirs.append(os.path.join("include", "Graphics", "GraphicsEngineD3D12", "interface"))

        self.cpp_info.defines.append("SPIRV_CROSS_NAMESPACE_OVERRIDE={}".format(self.dependencies["spirv-cross"].options.namespace))
        self.cpp_info.defines.append("{}=1".format(self._diligent_platform()))

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa', 'AppKit']
        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ["dxgi", "shlwapi"]
