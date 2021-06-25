import os
import glob
from conans import ConanFile, CMake, tools


class JsonnetConan(ConanFile):
    name = "jsonnet"
    version = "0.17.0"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/jsonnet"
    description = "Jsonnet - The data templating language"
    topics = ("conan", "jsonnet")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-" + self.version)[0]
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options["shared"]
        self._cmake.definitions["BUILD_JSONNET"] = False
        self._cmake.definitions["BUILD_JSONNETFMT"] = False
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        if not self.options["shared"]:
            for patch in self.conan_data.get("patches", {}).get(self.version, []):
                tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["jsonnet++", "jsonnet"]
        self.cpp_info.names["cmake_find_package"] = "jsonnet"
        self.cpp_info.names["cmake_find_package_multi"] = "jsonnet"
        self.cpp_info.names["pkg_config"] = "jsonnet"
