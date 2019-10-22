import os

from conans import CMake, ConanFile, tools


class LibsolaceConan(ConanFile):
    name = "libsolace"
    description = "High performance components for mission critical applications"
    topics = ("HPC", "High reliability", "P10", "solace", "performance", "c++", "conan")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/abbyssoul/libsolace"
    license = "Apache-2.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = "shared=False", "fPIC=True"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, parallel=True)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["PKG_CONFIG"] = "OFF"
        cmake.definitions["SOLACE_GTEST_SUPPORT"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["solace"]
