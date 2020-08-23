from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class QuickfixConan(ConanFile):
    name = "quickfix"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ssl":  [True, False],
               "with_postgres": [True, False],
               "with_mysql": [None, "libmysqlclient"]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": False,
                       "with_postgres": False,
                       "with_mysql": None}
    generators = "cmake"
    exports_sources = "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["HAVE_SSL"] = self.options.with_ssl
            self._cmake.definitions["HAVE_POSTGRESQL"] = self.options.with_postgres
            self._cmake.definitions["HAVE_MYSQL"] = bool(self.options.with_mysql)
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1g")

        if self.options.with_postgres:
            self.requires("libpq/11.5")

        if self.options.with_mysql == "libmysqlclient":
            self.requires("libmysqlclient/8.0.17")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("QuickFIX cannot be built as shared lib on Windows")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst=os.path.join("include", "quickfix"), src=self._build_subfolder)
        self.copy("Except.h", dst="include", src=os.path.join(self._source_subfolder, "src", "C++"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.with_ssl:
            self.cpp_info.defines.append("HAVE_SSL=1")

        if self.options.with_postgres:
            self.cpp_info.defines.append("HAVE_POSTGRESQL=1")

        if self.options.with_mysql:
            self.cpp_info.defines.append("HAVE_MYSQL=1")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread"])
