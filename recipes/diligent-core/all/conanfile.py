import os
from conans import ConanFile, tools, CMake


class DiligentCoreConan(ConanFile):
    name = "diligent-core"
    url = "https://github.com/DiligentGraphics/DiligentCore/"
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
    "with_glslang" : False
    }
    generators = "cmake_find_package", "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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
        self.requires("libtiff/4.2.0")
        self.requires("zlib/1.2.11")
        self.requires("libpng/1.6.37")

        self.requires("spirv-headers/cci.20210526")
        self.requires("spirv-tools/cci.20210601")
        self.requires("spirv-cross/cci.20210601")
        #self.requires("glslang/8.13.3559")
        
        self.requires("vulkan-memory-allocator/2.3.0")
        self.requires("vulkan-loader/1.2.172")
        self.requires("vulkan-headers/1.2.172")
        
        self.requires("glew/2.2.0")
        self.requires("stb/20200203")
        self.requires("volk/1.2.170")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DILIGENT_BUILD_SAMPLES"] = False
        self._cmake.definitions["DILIGENT_BUILD_TESTS"] = False
        self._cmake.definitions["DILIGENT_NO_FORMAT_VALIDATION"] = True
        self._cmake.definitions["DILIGENT_NO_GLSLANG"] = not self.options.with_glslang

        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
