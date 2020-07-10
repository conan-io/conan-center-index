from conans import ConanFile, tools
from conans.errors import ConanException


class ConanXOrg(ConanFile):
    name = "xorg"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://www.x.org/wiki/"
    description = "The X.Org project provides an open source implementation of the X Window System."
    settings = {"os": "Linux"}

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("OpenGL development files aren't available, give up")
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
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_apt:
                packages = ["xorg-dev", "libx11-xcb-dev", "libxcb-render0-dev", "libxcb-render-util0-dev"]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["xorg-x11-server-devel", "libfontenc-devel", "libXaw-devel",
                            "libXcomposite-devel", "libXcursor-devel", "libXdmcp-devel", "libXft-devel",
                            "libXtst-devel", "libXinerama-devel", "xorg-x11-xkb-utils-devel", "libXrandr-devel",
                            "libXres-devel", "libXScrnSaver-devel", "libXvMC-devel", "libXxf86dga-devel",
                            "xorg-x11-xtrans-devel", "xcb-util-wm-devel", "xcb-util-image-devel",
                            "xcb-util-keysyms-devel", "xcb-util-renderutil-devel"]
            elif tools.os_info.with_pacman:
                packages = ["xorg-server-devel"]
            elif tools.os_info.with_zypper:
                packages = ["Xorg-x11-devel"]
            else:
                self.output.warn("Do not know how to install 'xorg' for {}.".format(tools.os_info.linux_distro))
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        for name in ["x11", "x11-xcb", "dmx", "fontenc", "libfs", "ice", "sm", "xau", "xaw7",
                     "xcomposite","xcursor", "xdamage", "xdmcp", "xext", "xfixes", "xft", "xi",
                     "xinerama", "xkbfile", "xmu", "xmuu", "xpm", "xrandr", "xrender", "xres",
                     "xscrnsaver", "xt", "xtst", "xv", "xvmc", "xxf86dga", "xxf86vm", "xtrans"]:
            self._fill_cppinfo_from_pkgconfig(name)
