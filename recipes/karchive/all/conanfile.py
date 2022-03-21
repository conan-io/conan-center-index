import os
from conan.tools.files import rename
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class KArchiveConan(ConanFile):
    name = "karchive"
    license = ("BSD-2-Clause", "LGPL-2.0-only", "LGPL-2.0-or-later", "LGPL-3.0-only", "LicenseRef-KDE-Accepted-LGPL")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/frameworks/karchive/html/index.html"
    topics = ("archive", "compression")
    description = "KArchive provides classes for easy reading, creation and manipulation of archive formats like ZIP and TAR."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_lzma": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lzma": True
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("extra-cmake-modules/5.75.0")

    def requirements(self):
        self.requires("qt/5.15.2")
        self.requires("zlib/1.2.11")
        self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['ECM_MKSPECS_INSTALL_DIR'] = os.path.join(self.package_folder, "res")
        self._cmake.definitions['KDE_INSTALL_LOGGINGCATEGORIESDIR'] = os.path.join(self.package_folder, "res")
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*", src=os.path.join(self._source_subfolder, "LICENSES"), dst="licenses")

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "karchive")
        self.cpp_info.set_property("cmake_target_name", "karchive::karchive")
        self.cpp_info.set_property("cmake_find_mode", "both")

        self.cpp_info.libs = ["KF5Archive"]
        self.cpp_info.includedirs.extend([os.path.join("include", "KF5"), os.path.join("include", "KF5", "KArchive")])
