from conan import ConanFile
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"


class XorgConan(ConanFile):
    name = "xorg"
    package_type = "shared-library"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://www.x.org/wiki/"
    description = "The X.Org project provides an open source implementation of the X Window System."
    settings = "os", "arch", "compiler", "build_type"
    topics = ("x11", "xorg")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        apt = package_manager.Apt(self)
        apt.install(["libx11-dev", "libx11-xcb-dev", "libfontenc-dev", "libice-dev", "libsm-dev", "libxau-dev", "libxaw7-dev",
                     "libxcomposite-dev", "libxcursor-dev", "libxdamage-dev", "libxdmcp-dev", "libxext-dev", "libxfixes-dev",
                     "libxi-dev", "libxinerama-dev", "libxkbfile-dev", "libxmu-dev", "libxmuu-dev",
                     "libxpm-dev", "libxrandr-dev", "libxrender-dev", "libxres-dev", "libxss-dev", "libxt-dev", "libxtst-dev",
                     "libxv-dev", "libxvmc-dev", "libxxf86vm-dev", "libxcb-render0-dev",
                     "libxcb-render-util0-dev", "libxcb-xkb-dev", "libxcb-icccm4-dev", "libxcb-image0-dev",
                     "libxcb-keysyms1-dev", "libxcb-randr0-dev", "libxcb-shape0-dev", "libxcb-sync-dev", "libxcb-xfixes0-dev",
                     "libxcb-xinerama0-dev", "libxcb-dri3-dev", "uuid-dev", "libxcb-cursor-dev"], update=True, check=True)
        apt.install_substitutes(
            ["libxcb-util-dev"], ["libxcb-util0-dev"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["libxcb-devel", "libfontenc-devel", "libXaw-devel", "libXcomposite-devel",
                           "libXcursor-devel", "libXdmcp-devel", "libXtst-devel", "libXinerama-devel",
                           "libxkbfile-devel", "libXrandr-devel", "libXres-devel", "libXScrnSaver-devel", "libXvMC-devel",
                           "xcb-util-wm-devel", "xcb-util-image-devel", "xcb-util-keysyms-devel",
                           "xcb-util-renderutil-devel", "libXdamage-devel", "libXxf86vm-devel", "libXv-devel",
                           "xcb-util-devel", "libuuid-devel", "xcb-util-cursor-devel"], update=True, check=True)

        dnf = package_manager.Dnf(self)
        dnf.install(["libxcb-devel", "libfontenc-devel", "libXaw-devel", "libXcomposite-devel",
                           "libXcursor-devel", "libXdmcp-devel", "libXtst-devel", "libXinerama-devel",
                           "libxkbfile-devel", "libXrandr-devel", "libXres-devel", "libXScrnSaver-devel", "libXvMC-devel",
                           "xcb-util-wm-devel", "xcb-util-image-devel", "xcb-util-keysyms-devel",
                           "xcb-util-renderutil-devel", "libXdamage-devel", "libXxf86vm-devel", "libXv-devel",
                           "xcb-util-devel", "libuuid-devel", "xcb-util-cursor-devel"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libxcb-devel", "libfontenc-devel", "libXaw-devel", "libXcomposite-devel",
                              "libXcursor-devel", "libXdmcp-devel", "libXtst-devel", "libXinerama-devel",
                              "libxkbfile-devel", "libXrandr-devel", "libXres-devel", "libXss-devel", "libXvMC-devel",
                              "xcb-util-wm-devel", "xcb-util-image-devel", "xcb-util-keysyms-devel",
                              "xcb-util-renderutil-devel", "libXdamage-devel", "libXxf86vm-devel", "libXv-devel",
                              "xcb-util-devel", "libuuid-devel", "xcb-util-cursor-devel"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libxcb", "libfontenc", "libice", "libsm", "libxaw", "libxcomposite", "libxcursor",
                              "libxdamage", "libxdmcp", "libxtst", "libxinerama", "libxkbfile", "libxrandr", "libxres",
                              "libxss", "libxvmc", "xcb-util-wm", "xcb-util-image", "xcb-util-keysyms", "xcb-util-renderutil",
                              "libxxf86vm", "libxv", "xcb-util", "util-linux-libs", "xcb-util-cursor"], update=True, check=True)

        package_manager.Pkg(self).install(["libX11", "libfontenc", "libice", "libsm", "libxaw", "libxcomposite", "libxcursor",
                           "libxdamage", "libxdmcp", "libxtst", "libxinerama", "libxkbfile", "libxrandr", "libxres",
                           "libXScrnSaver", "libxvmc", "xcb-util-wm", "xcb-util-image", "xcb-util-keysyms", "xcb-util-renderutil",
                           "libxxf86vm", "libxv", "xkeyboard-config", "xcb-util", "xcb-util-cursor"], update=True, check=True)

    def package_info(self):
        for name in ["x11", "x11-xcb", "fontenc", "ice", "sm", "xau", "xaw7",
                     "xcomposite", "xcursor", "xdamage", "xdmcp", "xext", "xfixes", "xi",
                     "xinerama", "xkbfile", "xmu", "xmuu", "xpm", "xrandr", "xrender", "xres",
                     "xscrnsaver", "xt", "xtst", "xv", "xvmc", "xxf86vm", 
                     "xcb-xkb", "xcb-icccm", "xcb-image", "xcb-keysyms", "xcb-randr", "xcb-render",
                     "xcb-renderutil", "xcb-shape", "xcb-shm", "xcb-sync", "xcb-xfixes",
                     "xcb-xinerama", "xcb", "xcb-atom", "xcb-aux", "xcb-event", "xcb-util",
                     "xcb-dri3", "xcb-cursor"] + ([] if self.settings.os == "FreeBSD" else ["uuid"]):
            pkg_config = PkgConfig(self, name)
            pkg_config.fill_cpp_info(
                self.cpp_info.components[name], is_system=self.settings.os != "FreeBSD")
            self.cpp_info.components[name].version = pkg_config.version
            self.cpp_info.components[name].set_property(
                "pkg_config_name", name)
            self.cpp_info.components[name].set_property(
                "component_version", pkg_config.version)
            self.cpp_info.components[name].set_property("pkg_config_custom_content",
                                                        "\n".join(f"{key}={value}" for key, value in pkg_config.variables.items() if key not in ["pcfiledir","prefix", "includedir"]))

        if self.settings.os == "Linux":
            self.cpp_info.components["sm"].requires.append("uuid")
