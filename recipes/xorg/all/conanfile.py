from conans import ConanFile, tools
from conans.errors import ConanException

required_conan_version = ">=1.29"

class ConanXOrg(ConanFile):
    name = "xorg"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://www.x.org/wiki/"
    description = "The X.Org project provides an open source implementation of the X Window System."
    settings = {"os": "Linux"}
    topics = ("conan", "x11", "xorg")

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

        self.cpp_info.components[name].system_libs = libs
        self.cpp_info.components[name].libdirs = lib_dirs
        self.cpp_info.components[name].sharedlinkflags = ldflags
        self.cpp_info.components[name].exelinkflags = ldflags
        self.cpp_info.components[name].defines = defines
        self.cpp_info.components[name].includedirs = include_dirs
        self.cpp_info.components[name].cflags = cflags
        self.cpp_info.components[name].cxxflags = cflags
        self.cpp_info.components[name].version = pkg_config.version[0]

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_apt:
                packages = ["xorg-dev", "libx11-xcb-dev", "libxcb-render0-dev", "libxcb-render-util0-dev", "libxcb-xkb-dev",
                            "libxcb-icccm4-dev", "libxcb-image0-dev", "libxcb-keysyms1-dev", "libxcb-randr0-dev", "libxcb-shape0-dev",
                            "libxcb-sync-dev", "libxcb-xfixes0-dev", "libxcb-xinerama0-dev", "xkb-data"]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["libxcb-devel", "libfontenc-devel", "libXaw-devel", "libXcomposite-devel",
                            "libXcursor-devel", "libXdmcp-devel", "libXft-devel", "libXtst-devel", "libXinerama-devel",
                            "xorg-x11-xkb-utils-devel", "libXrandr-devel", "libXres-devel", "libXScrnSaver-devel", "libXvMC-devel",
                            "xorg-x11-xtrans-devel", "xcb-util-wm-devel", "xcb-util-image-devel", "xcb-util-keysyms-devel",
                            "xcb-util-renderutil-devel", "libXdamage-devel", "libXxf86vm-devel", "libXv-devel",
                            "xkeyboard-config-devel"]
            elif tools.os_info.with_pacman:
                packages = ["libxcb", "libfontenc", "libice", "libsm", "libxaw", "libxcomposite", "libxcursor",
                            "libxdamage", "libxdmcp", "libxft", "libxtst", "libxinerama", "libxkbfile", "libxrandr", "libxres",
                            "libxss", "libxvmc", "xtrans", "xcb-util-wm", "xcb-util-image","xcb-util-keysyms", "xcb-util-renderutil",
                            "libxxf86vm", "libxv", "xkeyboard-config"]
            elif tools.os_info.with_zypper:
                packages = ["xorg-x11-devel", "xcb-util-wm-devel", "xcb-util-image-devel", "xcb-util-keysyms-devel",
                            "xcb-util-renderutil-devel", "xkeyboard-config"]
            else:
                self.output.warn("Do not know how to install 'xorg' for {}.".format(tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        for name in ["x11", "x11-xcb", "fontenc", "ice", "sm", "xau", "xaw7",
                     "xcomposite", "xcursor", "xdamage", "xdmcp", "xext", "xfixes", "xft", "xi",
                     "xinerama", "xkbfile", "xmu", "xmuu", "xpm", "xrandr", "xrender", "xres",
                     "xscrnsaver", "xt", "xtst", "xv", "xvmc", "xxf86vm", "xtrans",
                     "xcb-xkb", "xcb-icccm", "xcb-image", "xcb-keysyms", "xcb-randr", "xcb-render",
                     "xcb-renderutil", "xcb-shape", "xcb-shm", "xcb-sync", "xcb-xfixes",
                     "xcb-xinerama", "xcb", "xkeyboard-config"]:
            self._fill_cppinfo_from_pkgconfig(name)
