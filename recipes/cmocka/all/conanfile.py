import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class CmockaConan(ConanFile):
    name = "cmocka"
    license = "Apache-2.0"
    homepage = "https://cmocka.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A unit testing framework for C"
    topics = ("unit_test", "unittest", "test", "testing", "mock", "mocking")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["WITH_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["WITH_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "CMocka"
        self.cpp_info.names["cmake_find_package_multi"] = "CMocka"
        self.cpp_info.names["pkg_config"] = "cmocka"
