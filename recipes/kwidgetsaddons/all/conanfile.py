import os
from conans import ConanFile, CMake, tools


class KwidgetsaddonsConan(ConanFile):
    name = "kwidgetsaddons"
    license = ("BSD-3-Clause", "LGPL-2.0-only", "LGPL-2.1-only", "LGPL-3.0-only", "LicenseRef-KDE-Accepted-LGPL", 
        "GPL-2.0-or-later", "LGPL-2.0-or-later", "LGPL-2.1-or-later", "LGPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/frameworks/kwidgetsaddons/html/index.html"
    topics = ("conan", "desktop", "widgets", "qt")
    description = "kwidgetsaddons contains add-on widgets and classes for applications that use the Qt Widgets module."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

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
        self.requires("qt/5.15.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("kwidgetsaddons-{}".format(self.version), self._source_subfolder)

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
            "KDE_INSTALL_DATADIR_KF5",
            "CONAN_KDE_INSTALL_DATADIR_KF5"
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['ECM_MKSPECS_INSTALL_DIR'] = os.path.join(self.package_folder, "res")
        self._cmake.definitions['KDE_INSTALL_LOGGINGCATEGORIESDIR'] = os.path.join(self.package_folder, "res")
        self._cmake.definitions['CONAN_KDE_INSTALL_DATADIR_KF5'] = os.path.join(self.package_folder, "res")
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
        self.cpp_info.libs = ["KF5WidgetsAddons"]
        self.cpp_info.includedirs = ["include/KF5", "include/KF5/KWidgetsAddons"]
        self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "plugins", "designer"))

