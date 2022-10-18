from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.system import package_manager
from conans import tools

required_conan_version = ">=1.47"


class SysConfigVAAPIConan(ConanFile):
    name = "vaapi"
    version = "system"
    description = "VA-API is an open-source library and API specification, which provides access to graphics hardware acceleration capabilities for video processing."
    topics = ("conan", "vaapi", "hwaccel", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://01.org/linuxmedia/vaapi"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("VAAPI development files aren't available, give up")
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
        dnf.install(["libva-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["libva-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libva-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libva"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libva-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libva"], update=True, check=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            for name in ['libva', 'libva-x11', 'libva-drm']:
                self._fill_cppinfo_from_pkgconfig(name)
