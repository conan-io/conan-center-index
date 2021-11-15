import os
from conans import ConanFile, tools, CMake


class DiligentCoreConan(ConanFile):
    name = "diligent-core"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentCore/tree/v2.5"
    description = "Diligent Core is a modern cross-platfrom low-level graphics API."
    license = ("Apache 2.0")
    topics = ("graphics")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
    "fPIC":         [True, False],
    "with_glslang": [True, False],
    }
    default_options = {"shared": False, 
    "fPIC": True,
    "with_glslang" : True
    }
    generators = "cmake_find_package", "cmake"
    _cmake = None
    exports_sources = ["CMakeLists.txt", "patches/**"]
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def requirements(self):
        self.requires("libjpeg/9d")
        self.requires("libtiff/4.3.0")
        self.requires("zlib/1.2.11")
        self.requires("libpng/1.6.37")

        self.requires("spirv-cross/cci.20210930")
        self.options["spirv-cross"].namespace = "diligent_spirv_cross"

        self.requires("spirv-headers/cci.20211010")
        self.requires("spirv-tools/2021.4")
        self.requires("glslang/11.7.0")
        self.requires("vulkan-headers/1.2.195")
        self.requires("volk/1.2.190")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            if not tools.cross_building(self, skip_x64_x86=True):
                self.requires("xkbcommon/1.3.0")        

    def diligent_platform(self):
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
        self._cmake.definitions["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang
        self._cmake.definitions["DILIGENT_NO_DIRECT3D11"] = True
        self._cmake.definitions["DILIGENT_NO_DIRECT3D12"] = True
        self._cmake.definitions["DILIGENT_NO_DXC"] = True

        self._cmake.definitions["ENABLE_RTTI"] = True
        self._cmake.definitions["ENABLE_EXCEPTIONS"] = True

        self._cmake.definitions[self.diligent_platform()] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self.settings.build_type == "Debug":
            self.cpp_info.libdirs.append("lib/source_subfolder/Debug")
        if self.settings.build_type == "Release":
            self.cpp_info.libdirs.append("lib/source_subfolder/Release")

        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "source_subfolder"))

        self.cpp_info.defines.append("SPIRV_CROSS_NAMESPACE_OVERRIDE=diligent_spirv_cross")
        self.cpp_info.defines.append("{}=1".format(self.diligent_platform()))

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa']
