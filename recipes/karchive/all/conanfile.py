import os
from conans import ConanFile, CMake, tools

class KArchiveConan(ConanFile):
    name = "karchive"
    license = ("BSD-2-Clause", "LGPL-2.0-only", "LGPL-2.0-or-later", "LGPL-3.0-only", "LicenseRef-KDE-Accepted-LGPL")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/frameworks/karchive/html/index.html"
    topics = ("conan", "archive", "compression")
    description = "KArchive provides classes for easy reading, creation and manipulation of archive formats like ZIP and TAR."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_bzip2": [True, False],
        "with_lzma": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "with_bzip2": True, "with_lzma": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_lzma
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("extra-cmake-modules/5.75.0")

    def requirements(self):
        self.requires("qt/5.15.1")
        self.requires("zlib/1.2.11")
        self.requires("bzip2/1.0.8")
        if self.settings.os == "Linux":
            self.requires("lzma/5.2.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("karchive-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['ECM_MKSPECS_INSTALL_DIR'] = os.path.join(self.package_folder, "res")
        self._cmake.definitions['KDE_INSTALL_LOGGINGCATEGORIESDIR'] = os.path.join(self.package_folder, "res")
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
        self.cpp_info.libs = ["KF5Archive"]
        self.cpp_info.includedirs = ['include/KF5', 'include/KF5/KArchive']

