import os
from conans import ConanFile, CMake, tools


class MuParserConan(ConanFile):
    name = "muparser"
    license = "BSD-2-Clause"
    homepage = "https://beltoforion.de/en/muparser/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("math", "parser",)
    description = "Fast Math Parser Library"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
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
        if self.options.with_openmp:
            self.output.warn("Conan package for OpenMP is not available, this package will be used from system.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SAMPLES"] = False
        self._cmake.definitions["ENABLE_OPENMP"] = self.options.with_openmp
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "muparser"
        self.cpp_info.names["cmake_find_package_multi"] = "muparser"
        self.cpp_info.names["pkg_config"] = "muparser"
        self.cpp_info.libs = ["muparser"]
        if not self.options.shared:
            self.cpp_info.defines = ["MUPARSER_STATIC=1"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
