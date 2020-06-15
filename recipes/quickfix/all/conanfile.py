from conans import ConanFile, CMake, tools
from conans.model.version import Version
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
               "shared_ptr": ["std", "tr1"],
               "unique_ptr": ["unique", "auto"]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": False,
                       "with_postgres": False,
                       "shared_ptr": "std",
                       "unique_ptr": "unique"}
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
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.settings.os != "Windows" and self.options.shared
            self._cmake.definitions["HAVE_SSL"] = self.options.with_ssl
            self._cmake.definitions["HAVE_POSTGRESQL"] = self.options.with_postgres
            self._cmake.definitions["SHARED_PTR"] = str(self.options.shared_ptr).upper()
            self._cmake.definitions["UNIQUE_PTR"] = str(self.options.unique_ptr).upper()
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared

        if hasattr(self.settings.compiler, "cppstd"):
            cppstd = str(self.settings.compiler.cppstd)
            if cppstd.find("17") != -1 or cppstd.find("20") != -1:
                self.options.unique_ptr = "unique"
            elif cppstd.find("98") != -1:
                self.options.unique_ptr = "auto"

        version = Version(str(self.settings.compiler.version))
        if self.settings.compiler == "Visual Studio" and (version <= "10" or self.settings.compiler.cppstd is None):
            self.options.shared_ptr = "tr1"

        if self.settings.compiler == "gcc" and str(self.settings.compiler.cppstd).find("98") != -1:
            self.options.shared_ptr = "tr1"

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src=self._source_subfolder)
        self.copy("Except.h", dst="include", src=os.path.join(self._source_subfolder, "src", "C++"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.with_ssl:
            self.cpp_info.defines.append("HAVE_SSL=1")

        if self.options.with_postgres:
            self.cpp_info.defines.append("HAVE_POSTGRESQL=1")

        if self.options.shared_ptr == "std":
            self.cpp_info.defines.append("HAVE_STD_SHARED_PTR=1")
        else:
            self.cpp_info.defines.append("HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER=1")

        if self.options.unique_ptr == "unique":
            self.cpp_info.defines.append("HAVE_STD_UNIQUE_PTR=1")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread"])
