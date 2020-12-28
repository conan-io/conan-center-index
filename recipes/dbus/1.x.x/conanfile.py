import os
import shutil
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class DbusConan(ConanFile):
    name = "dbus"
    license = ("AFL-2.1", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/dbus"
    description = "D-Bus is a simple system for interprocess communication and coordination."
    topics = ("conan", "dbus")
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "with_x11": [True, False],
        "with_glib": [True, False],
        "enable_assert": [True, False],
        "enable_checks": [True, False]}

    default_options = {
        "with_x11": False,
        "with_glib": False,
        "enable_assert": False,
        "enable_checks": False}

    generators = "cmake", "cmake_find_package"

    exports_sources = ["patches/*"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    _cmake = None

    def configure(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("dbus is only supported on Linux and FreeBSD")

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        tools.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("expat/2.2.10")
        if self.options.with_glib:
            self.requires("glib/2.67.0")

        if self.options.with_x11:
            self.requires("xorg/system")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)

            self._cmake.definitions["DBUS_BUILD_TESTS"] = False
            self._cmake.definitions["DBUS_ENABLE_DOXYGEN_DOCS"] = False
            self._cmake.definitions["DBUS_ENABLE_XML_DOCS"] = False

            self._cmake.definitions["DBUS_BUILD_X11"] = self.options.with_x11
            self._cmake.definitions["DBUS_WITH_GLIB"] = self.options.with_glib
            self._cmake.definitions["DBUS_DISABLE_ASSERT"] = not self.options.enable_assert
            self._cmake.definitions["DBUS_DISABLE_CHECKS"] = not self.options.enable_checks

            path_to_cmake_lists = os.path.join(self._source_subfolder, "cmake")

            self._cmake.configure(source_folder=path_to_cmake_lists,
                                  build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        for i in ["var", "share", "etc"]:
            shutil.move(os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: There should not be a namespace
        self.cpp_info.filenames["cmake_find_package"] = "DBus1"
        self.cpp_info.filenames["cmake_find_package_multi"] = "DBus1"
        self.cpp_info.names["cmake_find_package"] = "dbus-1"
        self.cpp_info.names["cmake_find_package_multi"] = "dbus-1"
        self.cpp_info.names["pkg_config"] = "dbus-1"

        self.cpp_info.includedirs.extend([
            "include/dbus-1.0", "lib/dbus-1.0/include"])
        self.cpp_info.libs = ["dbus-1"]
