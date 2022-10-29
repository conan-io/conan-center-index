from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.system import package_manager
from conans import tools

required_conan_version = ">=1.47"


class SysConfigEGLConan(ConanFile):
    name = "egl"
    version = "system"
    description = "cross-platform virtual conan package for the EGL support"
    topics = ("conan", "opengl", "egl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/egl"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipes supports only Linux and FreeBSD")

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("EGL development files aren't available, give up")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.system_libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_dirs)
        self.cpp_info.sharedlinkflags.extend(ldflags)
        self.cpp_info.exelinkflags.extend(ldflags)
        self.cpp_info.defines.extend(defines)
        self.cpp_info.includedirs.extend(include_dirs)
        self.cpp_info.cflags.extend(cflags)
        self.cpp_info.cxxflags.extend(cflags)

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["mesa-libEGL-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["mesa-libEGL-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        ubuntu_20_or_later = tools.os_info.linux_distro == "ubuntu" and tools.os_info.os_version >= "20"
        debian_11_or_later = tools.os_info.linux_distro == "debian" and tools.os_info.os_version >= "11"
        pop_os_20_or_later = tools.os_info.linux_distro == "pop" and tools.os_info.os_version >= "20"
        if ubuntu_20_or_later or debian_11_or_later or pop_os_20_or_later:
            apt.install(["libegl-dev"], update=True, check=True)
        else:
            apt.install(["libegl1-mesa-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libglvnd"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["Mesa-libEGL-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libglvnd"], update=True, check=True)

    def package_info(self):
        # TODO: Workaround for #2311 until a better solution can be found
        self.cpp_info.filenames["cmake_find_package"] = "egl_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "egl_system"

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self._fill_cppinfo_from_pkgconfig('egl')
