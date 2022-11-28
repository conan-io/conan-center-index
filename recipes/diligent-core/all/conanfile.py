from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import rm, get, rmdir, rename, collect_libs, patches, export_conandata_patches, copy, apply_conandata_patches
from conan.tools.apple import is_apple_os
import os

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
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=False)
        export_conandata_patches(self)
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=os.path.join(self.source_folder, "source_subfolder"), strip_root=True)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DILIGENT_BUILD_SAMPLES"] = False
        tc.variables["DILIGENT_NO_FORMAT_VALIDATION"] = True
        tc.variables["DILIGENT_BUILD_TESTS"] = False
        tc.variables["DILIGENT_NO_DXC"] = True
        tc.variables["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        tc.variables["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.options["spirv-cross"].namespace
        tc.variables["BUILD_SHARED_LIBS"] = False
        tc.variables["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        tc.variables["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_EXCEPTIONS"] = True
        tc.variables[self._diligent_platform()] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _patch_sources(self):
        patches.apply_conandata_patches(self)

    def build_requirements(self):
        self.tool_requires("cmake/3.24.2")

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("wayland/1.21.0")

        self.requires("spirv-cross/1.3.224.0")
        self.requires("spirv-tools/1.3.224.0")
        if self.options.with_glslang:
            self.requires("glslang/1.3.224.0")
        self.requires("vulkan-headers/1.3.224.1")
        self.requires("vulkan-validationlayers/1.3.224.1")
        self.requires("volk/1.3.224.1")
        self.requires("xxhash/0.8.1")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            if not cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.4.1")

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
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rename(self, src=os.path.join(self.package_folder, "include", "source_subfolder"),
        dst=os.path.join(self.package_folder, "include", "DiligentCore"))

        rmdir(self, os.path.join(self.package_folder, "Licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.package_folder, self.source_folder, "source_subfolder"))

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
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "DiligentCore", "Common"))

        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Common", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngine", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineVulkan", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineOpenGL", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsAccessories", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsTools", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "HLSL2GLSLConverterLib", "interface"))
        archiver_path = os.path.join("include", "DiligentCore", "Graphics", "Archiver", "interface")
        if os.path.isdir(archiver_path):
            self.cpp_info.includedirs.append(archiver_path)

        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Primitives", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Basic", "interface"))
        if self.settings.os == "Android":
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Android", "interface"))
        elif is_apple_os(self):
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Apple", "interface"))
        elif self.settings.os == "Emscripten":
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Emscripten", "interface"))
        elif self.settings.os == "Linux":
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Linux", "interface"))
        elif self.settings.os == "Windows":
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Platforms", "Win32", "interface"))
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineD3D11", "interface"))
            self.cpp_info.includedirs.append(os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineD3D12", "interface"))

        self.cpp_info.defines.append("SPIRV_CROSS_NAMESPACE_OVERRIDE={}".format(self.options["spirv-cross"].namespace))
        self.cpp_info.defines.append("{}=1".format(self._diligent_platform()))

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa', 'AppKit']
        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ["dxgi", "shlwapi"]
