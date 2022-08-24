import os

from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

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
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_cppstd(self):
        return ["17", "gnu17", "20", "gnu20"]

    def configure(self):
        compiler_version = tools.scm.Version(self, str(self.settings.compiler.version))

        if self.settings.os == "Windows":
          raise ConanInvalidConfiguration("This library is not yet compatible with Windows")
        # Exclude compilers that claims to support C++17 but do not in practice
        if (self.settings.compiler == "gcc" and compiler_version < "7") or \
           (self.settings.compiler == "clang" and compiler_version < "5") or \
           (self.settings.compiler == "apple-clang" and compiler_version < "9"):
          raise ConanInvalidConfiguration("This library requires C++17 or higher support standard. {} {} is not supported".format(self.settings.compiler, self.settings.compiler.version))
        if self.settings.compiler.cppstd and not self.settings.compiler.cppstd in self._supported_cppstd:
          raise ConanInvalidConfiguration("This library requires c++17 standard or higher. {} required".format(self.settings.compiler.cppstd))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, parallel=True)
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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
