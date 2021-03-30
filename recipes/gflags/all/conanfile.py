from conans import ConanFile, CMake, tools
import os


class GflagsConan(ConanFile):
    name = "gflags"
    description = "The gflags package contains a C++ library that implements commandline flags processing"
    topics = ("conan", "gflags", "cli", "flags", "commandline")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gflags/gflags"
    license = "BSD-3-Clause"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "nothreads": [True, False],
        "namespace": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "nothreads": True,
        "namespace": "gflags",
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_gflags_LIB"] = not self.options.nothreads
        self._cmake.definitions["BUILD_gflags_nothreads_LIB"] = self.options.nothreads
        self._cmake.definitions["BUILD_PACKAGING"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["INSTALL_HEADERS"] = True
        self._cmake.definitions["INSTALL_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["INSTALL_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["REGISTER_BUILD_DIR"] = False
        self._cmake.definitions["REGISTER_INSTALL_PREFIX"] = False
        self._cmake.definitions["GFLAGS_NAMESPACE"] = self.options.namespace
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["shlwapi"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "m"])
