from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class LogrConan(ConanFile):
    name = "logr"
    version = "0.1.0"
    license = "BSD 3-Clause License"
    homepage = "https://github.com/ngrodzitski/logr"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Logger frontend substitution for spdlog, glog, etc for server/desktop applications"
    topics = ("logger", "development", "util", "utils")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"
    exports_sources = ["CMakeLists.txt"]

    options = { 'spdlog_backend' : [True, False],
                'glog_backend' : [True, False],
                'log4cplus_backend' : [True, False] }

    default_options = { 'spdlog_backend': True,
                        'glog_backend': True,
                        'log4cplus_backend': True }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires( "fmt/7.1.2" )

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
        self._cmake.definitions['LOGR_WITH_SPDLOG_BACKEND'] = self.options.spdlog_backend
        self._cmake.definitions['LOGR_WITH_GLOG_BACKEND'] = self.options.glog_backend
        self._cmake.definitions['LOGR_WITH_LOG4CPLUS_BACKEND'] = self.options.log4cplus_backend

        self._cmake.definitions['LOGR_INSTALL'] = True

        self._cmake.configure(build_folder=self._build_subfolder)
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
        self.info.header_only()

    def package_info(self):
        self.info.header_only()
