import os
import shutil
from conans import AutoToolsBuildEnvironment, ConanFile, tools, CMake
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
        "with_glib": [True, False]}

    default_options = {
        "with_x11": False,
        "with_glib": False}

    generators = "pkg_config", "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    _autotools = None
    _cmake = None

    def configure(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            del self.options.with_x11

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("expat/2.4.1")
        if self.options.with_glib:
            self.requires("glib/2.68.2")

        if self.options.get_safe("with_x11", False):
            self.requires("xorg/system")

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)

            args = []
            args.append("--disable-tests")
            args.append("--disable-doxygen-docs")
            args.append("--disable-xml-docs")

            args.append("--%s-x11-autolaunch" % ("enable" if self.options.get_safe("with_x11", False) else "disable"))
            args.append("--disable-asserts")
            args.append("--disable-checks")

            args.append("--with-systemdsystemunitdir=%s" % os.path.join(self.package_folder, "lib", "systemd", "system"))
            args.append("--with-systemduserunitdir=%s" % os.path.join(self.package_folder, "lib", "systemd", "user"))

            args.append("--disable-launchd")
            args.append("--disable-systemd")

            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)

            self._cmake.definitions["DBUS_BUILD_TESTS"] = False
            self._cmake.definitions["DBUS_ENABLE_DOXYGEN_DOCS"] = False
            self._cmake.definitions["DBUS_ENABLE_XML_DOCS"] = False

            self._cmake.definitions["DBUS_BUILD_X11"] = self.options.get_safe("with_x11", False)
            self._cmake.definitions["DBUS_WITH_GLIB"] = self.options.with_glib
            self._cmake.definitions["DBUS_DISABLE_ASSERT"] = False
            self._cmake.definitions["DBUS_DISABLE_CHECKS"] = False

            path_to_cmake_lists = os.path.join(self._source_subfolder, "cmake")

            self._cmake.configure(source_folder=path_to_cmake_lists,
                                  build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "CMakeLists.txt"),
                              "project(dbus)",
                              "project(dbus)\ninclude(../../conanbuildinfo.cmake)\nconan_basic_setup()")
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share", "doc"))
        for i in ["var", "share", "etc"]:
            shutil.move(os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "systemd"))
        tools.remove_files_by_mask(self.package_folder, "*.la")

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
