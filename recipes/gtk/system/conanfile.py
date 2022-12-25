from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.system import package_manager
from conans import tools

required_conan_version = ">=1.47"


class ConanGTK(ConanFile):
    name = "gtk"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    homepage = "https://www.gtk.org"
    description = "A free and open-source cross-platform widget toolkit for creating graphical user interfaces"
    settings = "os", "arch", "compiler", "build_type"
    options = {"version": [2, 3]}
    default_options = {"version": 2}
    topics = ("gui", "widget", "graphical")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        self.info.settings.clear()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException(f"GTK-{self.options.version} development files aren't available, give up.")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.components[name].system_libs = libs
        self.cpp_info.components[name].libdirs = lib_dirs
        self.cpp_info.components[name].sharedlinkflags = ldflags
        self.cpp_info.components[name].exelinkflags = ldflags
        self.cpp_info.components[name].defines = defines
        self.cpp_info.components[name].includedirs = include_dirs
        self.cpp_info.components[name].cflags = cflags
        self.cpp_info.components[name].cxxflags = cflags

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libgtk2.0-dev"] if self.options.version == 2 else ["libgtk-3-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install([f"gtk{self.options.version}"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install([f"gtk{self.options.version}-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install([f"gtk{self.options.version}"], update=True, check=True)

    def package_info(self):
        for name in [f"gtk+-{self.options.version}.0"]:
            self._fill_cppinfo_from_pkgconfig(name)
