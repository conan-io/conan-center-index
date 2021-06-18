import os
import shutil
from conans import AutoToolsBuildEnvironment, ConanFile, tools
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

    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def configure(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("dbus is only supported on Linux and FreeBSD")

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("expat/2.4.1")
        if self.options.with_glib:
            self.requires("glib/2.68.2")

        if self.options.with_x11:
            self.requires("xorg/system")

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)

            args = []
            args.append("--disable-tests")
            args.append("--disable-doxygen-docs")
            args.append("--disable-xml-docs")

            args.append("--%s-x11-autolaunch" % ("enable" if self.options.with_x11 else "disable"))
            args.append("--disable-asserts")
            args.append("--disable-checks")

            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        for i in ["var", "share", "etc"]:
            shutil.move(os.path.join(self.package_folder, i), os.path.join(self.package_folder, "res", i))

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
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
