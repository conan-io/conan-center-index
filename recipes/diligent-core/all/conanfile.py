import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import rm, get, rmdir, collect_libs, export_conandata_patches, copy, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DiligentCoreConan(ConanFile):
    name = "diligent-core"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentCore"
    description = "Diligent Core is a modern cross-platform low-level graphics API."
    license = "Apache-2.0"
    topics = ("graphics",)
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC":   [True, False],
        "with_glslang": [True, False],
    }
    default_options = {
        "shared": False	,
        "fPIC": True,
        "with_glslang": False  # FIXME: fails with a compilation error on newer versions of glslang
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
        return 17

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        if is_msvc(self.info):
            if is_msvc_static_runtime(self.info):
                self.info.settings.compiler.runtime = "MT/MTd"
            else:
                self.info.settings.compiler.runtime = "MD/MDd"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        vulkan_sdk_version = "1.3.268.0"
        self.requires(f"spirv-cross/{vulkan_sdk_version}")
        self.requires(f"spirv-headers/{vulkan_sdk_version}")
        self.requires(f"spirv-tools/{vulkan_sdk_version}")
        if self.options.with_glslang:
            self.requires(f"glslang/{vulkan_sdk_version}")
        self.requires(f"vulkan-headers/{vulkan_sdk_version}")
        self.requires(f"vulkan-validationlayers/{vulkan_sdk_version}")
        self.requires(f"volk/{vulkan_sdk_version}")

        self.requires("opengl/system")
        self.requires("xxhash/0.8.2")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("wayland/1.22.0")
            self.requires("xorg/system")
            if not cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.6.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DILIGENT_BUILD_SAMPLES"] = False
        tc.variables["DILIGENT_NO_FORMAT_VALIDATION"] = True
        tc.variables["DILIGENT_BUILD_TESTS"] = False
        tc.variables["DILIGENT_NO_DXC"] = True
        tc.variables["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        tc.variables["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.dependencies["spirv-cross"].options.namespace
        tc.variables["BUILD_SHARED_LIBS"] = False
        tc.variables["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        tc.variables["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_EXCEPTIONS"] = True
        tc.variables[self._diligent_platform()] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "project(DiligentCore)",
                        "project(DiligentCore)\n\ninclude(conan_deps.cmake)")
        # Let Conan set the C++ standard
        if Version(self.version) >= "2.5.4":
            build_utils = os.path.join(self.source_folder, "BuildTools", "CMake", "BuildUtils.cmake")
        else:
            build_utils = os.path.join(self.source_folder, "BuildUtils.cmake")
        replace_in_file(self, build_utils, "CXX_STANDARD 14", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        os.rename(os.path.join(self.package_folder, "include"),
                  os.path.join(self.package_folder, "DiligentCore"))
        os.mkdir(os.path.join(self.package_folder, "include"))
        os.rename(os.path.join(self.package_folder, "DiligentCore"),
                  os.path.join(self.package_folder, "include", "DiligentCore"))

        rmdir(self, os.path.join(self.package_folder, "Licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.package_folder)

        if self.options.shared:
            copy(self, "*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, "*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
            rm(self, os.path.join(self.package_folder, "lib"), "*.a", recursive=True)
            if self.settings.os != "Windows":
                rm(self, os.path.join(self.package_folder, "lib"), "*.lib", recursive=True)
        else:
            copy(self, "*.a",   dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            rm(self, os.path.join(self.package_folder, "lib"), "*.dylib", recursive=True)
            rm(self, os.path.join(self.package_folder, "lib"), "*.so", recursive=True)
            rm(self, os.path.join(self.package_folder, "lib"), "*.dll", recursive=True)

        copy(self, "*.fxh", dst=os.path.join(self.package_folder, "res"), src=self.source_folder, keep_path=False)
        copy(self, "File2String*",  dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        # MinGw creates many invalid files, called objects.a, remove them here:
        rm(self, "objects.a", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.resdirs = ["res"]

        # included as discussed here https://github.com/conan-io/conan-center-index/pull/10732#issuecomment-1123596308
        self.cpp_info.includedirs += [
            os.path.join(self.package_folder, "include"),
            os.path.join(self.package_folder, "include", "DiligentCore", "Common"),
            os.path.join("include", "DiligentCore"),
            os.path.join("include", "DiligentCore", "Common", "interface"),
            os.path.join("include", "DiligentCore", "Platforms", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngine", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineVulkan", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "GraphicsEngineOpenGL", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "GraphicsAccessories", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "GraphicsTools", "interface"),
            os.path.join("include", "DiligentCore", "Graphics", "HLSL2GLSLConverterLib", "interface"),
        ]

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

        self.cpp_info.defines.append("SPIRV_CROSS_NAMESPACE_OVERRIDE={}".format(self.dependencies["spirv-cross"].options.namespace))
        self.cpp_info.defines.append("{}=1".format(self._diligent_platform()))

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Cocoa", "AppKit"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["dxgi", "shlwapi"]
