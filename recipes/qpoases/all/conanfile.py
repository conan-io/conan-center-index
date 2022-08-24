import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake


class ConanRecipe(ConanFile):
    name = "qpoases"

    description = "Open-source C++ implementation of the recently proposed online active set strategy."
    topics = ("conan", "container", "parametric", "quadratic", "programming")

    homepage = "https://github.com/coin-or/qpOASES"
    url = "https://github.com/conan-io/conan-center-index"

    license = "LGPL-2.1"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "qpOASES-releases-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["QPOASES_BUILD_EXAMPLES"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "qpOASES"
        self.cpp_info.names["cmake_find_package_multi"] = "qpOASES"

        self.cpp_info.libs = tools.collect_libs(self)
