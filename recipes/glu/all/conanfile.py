from conan import ConanFile
from conan.errors import ConanException
from conans import tools


class SysConfigGLUConan(ConanFile):
    name = "glu"
    version = "system"
    description = "cross-platform virtual conan package for the GLU support"
    topics = ("opengl", "glu")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cgit.freedesktop.org/mesa/glu/"
    license = "SGI-B-2.0"
    settings = "os"
    requires = "opengl/system"

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["mesa-libGLU-devel"]
            elif tools.os_info.with_apt:
                packages = ["libglu1-mesa-dev"]
            elif tools.os_info.with_pacman:
                packages = ["glu"]
            elif tools.os_info.with_zypper:
                packages = ["glu-devel"]
            else:
                self.output.warn("Don't know how to install GLU for your distro")
        if tools.os_info.is_freebsd and self.settings.os == "FreeBSD":
            packages = ["libGLU"]
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            for p in packages:
                package_tool.install(update=True, packages=p)

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("GLU development files aren't available, giving up")
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

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Glu32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self._fill_cppinfo_from_pkgconfig("glu")

    def package_id(self):
        self.info.header_only()
