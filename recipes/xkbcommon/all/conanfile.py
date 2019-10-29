from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("conan", "xkbcommon", "keyboard")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xkbcommon/libxkbcommon"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "docs": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": False,
        "docs": False
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _system_package_architecture(self):
        if not tools.cross_building(self.settings):
            return ""

        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ":i386"
            elif self.settings.arch == "x86_64":
                return ":amd64"
            elif self.settings.arch == "armv6" or self.settings.arch == "armv7":
                return ":armel"
            elif self.settings.arch == "armv7hf":
                return ":armhf"
            elif self.settings.arch == "armv8":
                return ":arm64"

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return ".i686"
            elif self.settings.arch == "x86_64":
                return ".x86_64"
        return ""

    def _system_package_name(self, package):
        return package + self._system_package_architecture()

    def system_requirements(self):
        pack_names = []
        if tools.os_info.with_apt:
            pack_names.append(self._system_package_name("xkb-data"))
            if self.options.with_x11:
                pack_names.extend([self._system_package_name("libxcb-xkb-dev"),
                                   self._system_package_name("libxcb1-dev")])
        elif tools.os_info.with_yum:
            pack_names.append(self._system_package_name("xkeyboard-config"))
            if self.options.with_x11:
                pack_names.append(self._system_package_name("libxcb-devel"))

        if pack_names:
            installer = tools.SystemPackageTool()
            for item in pack_names:
                installer.install(item)

    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.52.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libxkbcommon-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        meson.configure(
            defs={
                "enable-wayland": self.options.with_wayland,
                "enable-docs": self.options.docs,
                "enable-x11": self.options.with_x11,
                "libdir": os.path.join(self.package_folder, "lib"),
                "default_library": ("shared" if self.options.shared else "static")
            },
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.with_x11:
            self.cpp_info.libs.append("xcb")
            self.cpp_info.libs.append("xcb-xkb")
