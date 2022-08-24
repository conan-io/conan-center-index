from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

class LogrConan(ConanFile):
    name = "logr"
    license = "BSD 3-Clause License"
    homepage = "https://github.com/ngrodzitski/logr"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Logger frontend substitution for spdlog, glog, etc for server/desktop applications"
    topics = ("logger", "development", "util", "utils")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt"]

    options = { "backend": ["spdlog", "glog", "log4cplus", "log4cplus-unicode", None] }
    default_options = { "backend": "spdlog"}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("fmt/7.1.2")

        if self.options.backend == "spdlog":
            self.requires("spdlog/1.8.0")
        elif self.options.backend == "glog":
            self.requires("glog/0.4.0")
        elif self.options.backend == "log4cplus":
            self.requires("log4cplus/2.0.5")
        elif self.options.backend == "log4cplus-unicode":
            self.requires("log4cplus/2.0.5")

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "16"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["LOGR_WITH_SPDLOG_BACKEND"] = self.options.backend == "spdlog"
        self._cmake.definitions["LOGR_WITH_GLOG_BACKEND"] = self.options.backend == "glog"
        self._cmake.definitions["LOGR_WITH_LOG4CPLUS_BACKEND"] = self.options.backend in ["log4cplus", "log4cplus-unicode"]

        self._cmake.definitions["LOGR_INSTALL"] = True

        self._cmake.configure( build_folder=self._build_subfolder )
        return self._cmake

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.options.backend == "log4cplus" and self.options["log4cplus"].unicode:
            raise ConanInvalidConfiguration("backend='log4cplus' requires log4cplus:unicode=False")
        elif self.options.backend == "log4cplus-unicode" and not self.options["log4cplus"].unicode:
            raise ConanInvalidConfiguration("backend='log4cplus-unicode' requires log4cplus:unicode=True")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
