from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibModManConan(ConanFile):
    name = "libmodman"
    description = "libmodman is a simple library for managing C++ modules (plug-ins)."
    topics = ("conan", "libmodman", "plugin", "manager", "module")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://code.google.com/archive/p/libmodman/"
    license = "LGPL-2.1-or-later"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def  _build_subfolder(self):
        return "build_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio" and self.options.shared and self.settings.build_type == "Debug" and self.settings.compiler.version <= "14":
            raise ConanInvalidConfiguration("Cannot build a debug libmodman on MSVC <= 2015 (because test_package fails)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libmodman-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        prefix = self.package_folder.replace("\\", "/")
        self._cmake.definitions["CMAKE_INSTALL_PREFIX"] = "{}".format(prefix)
        self._cmake.definitions["INCLUDE_INSTALL_DIR"] = "{}/include".format(prefix)
        self._cmake.definitions["LIB_INSTALL_DIR"] = "{}/lib".format(prefix)
        self._cmake.definitions["BIN_INSTALL_DIR"] = "{}/bin".format(prefix)
        self._cmake.definitions["LIBEXEC_INSTALL_DIR"] = "{}/lib/libexec".format(prefix)
        self._cmake.definitions["SHARE_INSTALL_DIR"] = "{}/share".format(prefix)
        self._cmake.definitions["SYSCONF_INSTALL_DIR"] = "{}/share".format(prefix)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["modman"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m"]
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["WIN32"]

        self.cpp_info.names["pkg_config"] = "libmodman-2.0"
        self.cpp_info.names["cmake_find_package"] = "libmodman"  # FIXME: generates `libmodman` target (not `libmodman::libmodman`)
