import os
from conans import ConanFile, CMake, tools

class KcodecsConan(ConanFile):
    name = "kcodecs"
    license = (
        "BSD-3-Clause", "GPL-2.0-or-later", "LGPL-2.0-only", "LGPL-2.0-or-later", 
        "LGPL-2.1-or-later", "MIT", "MPL-1.1")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/frameworks/kcodecs/html/index.html"
    topics = ("conan", "kde", "encodings", "strings")
    description = "KCodecs provide a collection of methods to manipulate strings using various encodings."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
    }
    default_options = {'shared': False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("extra-cmake-modules/5.75.0")

    def requirements(self):
        self.requires("gperf/3.1")
        self.requires("qt/5.15.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("kcodecs-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['ECM_MKSPECS_INSTALL_DIR'] = os.path.join(self.package_folder, "res", "mkspecs", "modules")
        self._cmake.definitions['KDE_INSTALL_LOGGINGCATEGORIESDIR'] = os.path.join(self.package_folder, "res", "qlogging-categories5")
        self._cmake.definitions['CMAKE_INSTALL_LOCALEDIR'] = os.path.join(self.package_folder, "res", "locale")
        # a hack to avoid installing CMake find modules andconfig files (KB-H016)
        self._cmake.definitions['KDE_INSTALL_CMAKEPACKAGEDIR'] = os.path.join(self.build_folder, "dummy")
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*", src=os.path.join(self._source_subfolder, "LICENSES"), dst="licenses")


    def package_info(self):
        self.cpp_info.libs = ["KF5Codecs"]
        self.cpp_info.includedirs = ['include/KF5', 'include/KF5/KCodecs']

