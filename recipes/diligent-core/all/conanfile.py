from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
from conan.tools.build import cross_building

required_conan_version = ">=1.33.0"


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
    generators = "cmake_find_package", "cmake", "cmake_find_package_multi"
    _cmake = None
    exports_sources = ["CMakeLists.txt", "patches/**"]
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.scm.Version(self, self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build_requirements(self):
        self.build_requires("cmake/3.22.0")

    def requirements(self):
        self.requires("opengl/system")

        self.requires("spirv-cross/1.3.216.0")
        self.requires("spirv-tools/1.3.216.0")
        if self.options.with_glslang:
            self.requires("glslang/1.3.216.0")
        self.requires("vulkan-headers/1.3.216.0")
        self.requires("vulkan-validationlayers/1.3.216.0")
        self.requires("volk/1.3.216.0")
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DILIGENT_BUILD_SAMPLES"] = False
        self._cmake.definitions["DILIGENT_NO_FORMAT_VALIDATION"] = True
        self._cmake.definitions["DILIGENT_BUILD_TESTS"] = False
        self._cmake.definitions["DILIGENT_NO_DXC"] = True
        self._cmake.definitions["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        self._cmake.definitions["SPIRV_CROSS_NAMESPACE_OVERRIDE"] = self.options["spirv-cross"].namespace
        self._cmake.definitions["BUILD_SHARED_LIBS"] = False
        self._cmake.definitions["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        self._cmake.definitions["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""

        self._cmake.definitions["ENABLE_RTTI"] = True
        self._cmake.definitions["ENABLE_EXCEPTIONS"] = True

        self._cmake.definitions[self._diligent_platform()] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rename(self, src=os.path.join(self.package_folder, "include", "source_subfolder"),
        dst=os.path.join(self.package_folder, "include", "DiligentCore"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "Licenses"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)

        if self.options.shared:
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            self.copy(pattern="*.so", dst="lib", keep_path=False)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.a")
            if self.settings.os != "Windows":
                tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.lib")
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.dylib")
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.so")
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.dll")

        self.copy(pattern="*.fxh", dst="res", keep_path=False)

        self.copy("File2String*", src=os.path.join(self._build_subfolder, "bin"), dst="bin", keep_path=False)
        tools.files.rm(self, self.package_folder, "*.pdb")
        # MinGw creates many invalid files, called objects.a, remove them here:
        tools.files.rm(self, self.package_folder, "objects.a")

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
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
        elif tools.apple.is_apple_os(self, self.settings.os):
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
