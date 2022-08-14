from conans import ConanFile, CMake
from conan.tools.files import get


class OctoLoggerCPPConan(ConanFile):
    name = "octo-logger-cpp"
    license = "MIT"
    url = "https://github.com/ofiriluz/octo-logger-cpp"
    homepage = "https://github.com/ofiriluz/octo-logger-cpp"
    description = "Octo logger library"
    topics = ("logging", "cpp")
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "build"

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("catch2/3.1.0")
        self.requires("fmt/9.0.0")
        self.requires("trompeloeil/42")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.build(build_dir=self._build_subfolder)
        cmake.test(build_dir=self._build_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "octo-logger-cpp")
        self.cpp_info.set_property("cmake_target_name", "octo-logger-cpp::octo-logger-cpp")
        self.cpp_info.set_property("pkg_config_name", "octo-logger-cpp")
        self.cpp_info.components["octo-logger-cpp"].libs = ["octo-logger-cpp"]
        self.cpp_info.components["octo-logger-cpp"].requires = [
            "catch2::catch2",
            "fmt::fmt",
            "trompeloeil::trompeloeil"
        ]
        self.cpp_info.filenames["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.names["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.names["pkg_config"] = "octo-logger-cpp"
        self.cpp_info.components["octo-logger-cpp"].names["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.components["octo-logger-cpp"].names["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.components["octo-logger-cpp"].set_property("cmake_target_name", "octo-logger-cpp::octo-logger-cpp")
        self.cpp_info.components["octo-logger-cpp"].set_property("pkg_config_name", "octo-logger-cpp")
