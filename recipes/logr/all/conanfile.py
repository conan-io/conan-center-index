from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os


class LogrConan(ConanFile):
    name = "logr"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ngrodzitski/logr"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "Logger frontend substitution for spdlog, glog, etc "
        "for server/desktop applications"
    )
    topics = ("logger", "development", "util", "utils")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    options = {"backend": ["spdlog", "glog", "log4cplus", "boostlog", None]}
    default_options = {"backend": "spdlog"}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("fmt/8.1.1")

        if self.options.backend == "spdlog":
            self.requires("spdlog/1.9.2")
        elif self.options.backend == "glog":
            self.requires("glog/0.5.0")
        elif self.options.backend == "log4cplus":
            self.requires("log4cplus/2.0.5")
        elif self.options.backend == "boostlog":
            self.requires("boost/1.77.0")

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "16",
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                (
                    "%s recipe lacks information about the %s compiler "
                    "standard version support"
                )
                % (self.name, compiler)
            )
            self.output.warn(
                "%s requires a compiler that supports at least C++%s"
                % (self.name, minimal_cpp_standard)
            )
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s"
                % (self.name, minimal_cpp_standard)
            )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["LOGR_WITH_SPDLOG_BACKEND"] = (
            self.options.backend == "spdlog"
        )
        self._cmake.definitions["LOGR_WITH_GLOG_BACKEND"] = (
            self.options.backend == "glog"
        )
        self._cmake.definitions["LOGR_WITH_LOG4CPLUS_BACKEND"] = (
            self.options.backend == "log4cplus"
        )
        self._cmake.definitions["LOGR_WITH_BOOSTLOG_BACKEND"] = (
            self.options.backend == "boostlog"
        )

        self._cmake.definitions["LOGR_INSTALL"] = True
        self._cmake.definitions["LOGR_CONAN_PACKAGING"] = True
        self._cmake.definitions["LOGR_BUILD_TESTS"] = False
        self._cmake.definitions["LOGR_BUILD_EXAMPLES"] = False
        self._cmake.definitions["LOGR_BUILD_BENCHMARKS"] = False

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.settings.clear()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "logr"
        self.cpp_info.names["cmake_find_package_multi"] = "logr"

        self.cpp_info.components["logr_base"].includedirs = ["include"]
        self.cpp_info.components["logr_base"].requires = ["fmt::fmt"]

        if self.options.backend == "spdlog":
            self.cpp_info.components["logr_spdlog"].includedirs = []
            self.cpp_info.components["logr_spdlog"].requires = [
                "logr_base",
                "spdlog::spdlog",
            ]
        elif self.options.backend == "glog":
            self.cpp_info.components["logr_glog"].includedirs = []
            self.cpp_info.components["logr_glog"].requires = [
                "logr_base",
                "glog::glog",
            ]
        elif self.options.backend == "log4cplus":
            self.cpp_info.components["logr_log4cplus"].includedirs = []
            self.cpp_info.components["logr_log4cplus"].requires = [
                "logr_base",
                "log4cplus::log4cplus",
            ]
        elif self.options.backend == "boostlog":
            self.cpp_info.components["logr_boostlog"].includedirs = []
            self.cpp_info.components["logr_boostlog"].requires = [
                "logr_base",
                "boost::log",
            ]
