from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import rm, get, rmdir, rename, collect_libs, export_conandata_patches, copy, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import visual
from conan.tools.apple import is_apple_os
import os
from pathlib import Path
required_conan_version = ">=1.52.0"


class DiligentCoreConan(ConanFile):
    name = "diligent-core"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentCore"
    description = "Diligent Core is a modern cross-platfrom low-level graphics API."
    license = "Apache-2.0"
    topics = ("graphics")
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
    short_paths = True

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "6",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    @property
    def _minimum_cpp_standard(self):
        return 14

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if visual.is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")

    def export_sources(self):
        copy(self, "conan_deps.cmake", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"), keep_path=False)
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        if visual.is_msvc(self.info):
            if visual.is_msvc_static_runtime(self.info):
                self.info.settings.compiler.runtime = "MT/MTd"
            else:
                self.info.settings.compiler.runtime = "MD/MDd"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DILIGENT_BUILD_SAMPLES"] = False
        tc.variables["DILIGENT_NO_FORMAT_VALIDATION"] = True
        tc.variables["DILIGENT_BUILD_TESTS"] = False
        tc.variables["DILIGENT_NO_DXC"] = True
        tc.variables["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        #tc.variables["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.dependencies["spirv-cross"].options.namespace
        tc.variables["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        tc.variables["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_EXCEPTIONS"] = True
        tc.variables["DILIGENT_BUILD_CORE_THIRD_PARTY"] = False
        spirv_tools_package = Path(self.dependencies["spirv-tools"].package_folder)

        # ...\spirv-tools\<hash>\p
        # -> ...\spirv-tools\<hash>\b\src
        spirv_tools_src = (
            spirv_tools_package.parent / "b" / "src"
        ).as_posix()

        spirv_tools_include = (
            Path(spirv_tools_src) / "include"
        ).as_posix()

        spirv_tools_build = (
            spirv_tools_package.parent / "b" / "build"
        ).as_posix()

        print(f"SPIRV-Tools source directory: {spirv_tools_src}")
        print(f"SPIRV-Tools include directory: {spirv_tools_include}")
        print(f"SPIRV-Tools build directory: {spirv_tools_build}")

        tc.variables["CONAN_SPIRV_TOOLS_SOURCE_DIR"] = spirv_tools_src
        tc.variables["CONAN_SPIRV_TOOLS_INCLUDE_DIR"] = spirv_tools_include
        tc.variables["CONAN_SPIRV_TOOLS_BUILD_DIR"] = spirv_tools_build

        spirv_headers_package = Path(
            self.dependencies["spirv-headers"].package_folder
        )

        spirv_headers_include = (
            spirv_headers_package / "include"
        ).as_posix()
        spirv_headers_unified_include = (
                    spirv_headers_package / "include" / "spirv" / "unified1"
                ).as_posix()
        print(f"SPIRV-Headers include directory: {spirv_headers_include}")
        print(f"SPIRV-Headers unified include directory: {spirv_headers_unified_include}")

        tc.variables["CONAN_SPIRV_HEADERS_INCLUDE_DIR"] = spirv_headers_include
        tc.variables["CONAN_SPIRV_HEADERS_UNIFIED_INCLUDE_DIR"] = spirv_headers_unified_include
        tc.variables["DILIGENT_USE_VOLK"] = True
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["VK_USE_PLATFORM_WIN32_KHR"] = True
        tc.variables[self._diligent_platform()] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "project(DiligentCore)",
                        "project(DiligentCore)\n\ninclude(conan_deps.cmake)")
        replace_in_file(
            self,
            os.path.join(self.source_folder, "ThirdParty", "CMakeLists.txt"),
            "if (NOT ${DILIGENT_NO_GLSLANG} AND (NOT TARGET glslang))",
            "if (NOT ${DILIGENT_NO_GLSLANG} AND (NOT TARGET glslang AND NOT TARGET glslang::glslang))"
        )

        # 2. Disable USE_SPIRV_TOOLS in ShaderTools (prevents missing source/opt/pass.h)


    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("wayland/1.24.0")

        self.requires("spirv-headers/1.4.350.0")
        self.requires("spirv-cross/1.4.350.0")
        self.requires("spirv-tools/1.4.350.0")
        if self.options.with_glslang:
            self.requires("glslang/1.4.350.0")
        self.requires("vulkan-headers/1.4.350.0")
        self.requires("vulkan-validationlayers/1.4.350.0")
        self.requires("volk/1.4.350.0")
        self.requires("xxhash/0.8.3")
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
        self._patch_sources()
        cmake = CMake(self)
        # By default, Diligent builds static and shared versions of every main library. We select the one we
        # want based on options.shared in package(). To avoid building every intermediate library as SHARED,
        # we have to disable BUILD_SHARED_LIBS.
        # However, BUILD_SHARED_LIBS cannot be disabled normally (in the toolchain in configure()), because
        # Conan outputs that override after the standard line that enables BUILD_SHARED_LIBS. Since the latter
        # is a CACHE variable that cannot be overwritten with another set(), we have to specify it on the
        # command-line, so it takes effect before the toolchain is parsed.
        cmake.configure(variables={"BUILD_SHARED_LIBS": "OFF"})
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
        self.cpp_info.includedirs.append(os.path.join("src"))
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

        #self.cpp_info.defines.append("SPIRV_CROSS_NAMESPACE_OVERRIDE={}".format(self.dependencies["spirv-cross"].options.namespace))
        self.cpp_info.defines.append("{}=1".format(self._diligent_platform()))

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa', 'AppKit']
        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ["dxgi", "shlwapi"]

