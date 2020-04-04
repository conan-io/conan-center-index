import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class ExpressCppConan(ConanFile):
    name = "expresscpp"
    description = "Fast, unopinionated, minimalist web framework for C++ Perfect for building REST APIs"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/expresscpp/expresscpp"
    topics = ("conan", "expresscpp", "logging", "header-only")
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires.add("boost/1.72.0")
        self.requires.add("fmt/6.1.2")
        self.requires.add("nlohmann_json/3.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "expresscpp", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
