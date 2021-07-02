import os

from conans import ConanFile, CMake, tools

class ShadercConan(ConanFile):
    name = "shaderc"
    description = "A collection of tools, libraries and tests for shader compilation."
    license = "Apache-2.0"
    topics = ("conan", "shaderc", "glsl", "hlsl", "msl", "spirv", "spir-v", "glslc", "spvc")
    homepage = "https://github.com/google/shaderc"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "spvc": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "spvc": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("glslang/8.13.3559")
        self.requires("spirv-tools/2020.5")
        if self.options.spvc:
           self.requires("spirv-cross/20210115")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["SHADERC_ENABLE_SPVC"] = self.options.spvc
        self._cmake.definitions["SHADERC_SKIP_INSTALL"] = False
        self._cmake.definitions["SHADERC_SKIP_TESTS"] = True
        self._cmake.definitions["SHADERC_SPVC_ENABLE_DIRECT_LOGGING"] = False
        self._cmake.definitions["SHADERC_SPVC_DISABLE_CONTEXT_LOGGING"] = False
        self._cmake.definitions["SHADERC_ENABLE_WERROR_COMPILE"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["SHADERC_ENABLE_SHARED_CRT"] = str(self.settings.compiler.runtime).startswith("MD")
        self._cmake.definitions["ENABLE_CODE_COVERAGE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "shaderc" if self.options.shared else "shaderc_static"
        self.cpp_info.libs = self._get_ordered_libs()
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
        if self.options.shared:
            self.cpp_info.defines.append("SHADERC_SHAREDLIB")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

    def _get_ordered_libs(self):
        libs = ["shaderc_shared" if self.options.shared else "shaderc"]
        if not self.options.shared:
            libs.append("shaderc_util")
        if self.options.spvc:
            libs.append("shaderc_spvc_shared" if self.options.shared else "shaderc_spvc")
        return libs
