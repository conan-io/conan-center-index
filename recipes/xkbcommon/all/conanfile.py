from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("conan", "xkbcommon", "keyboard")
    url = "https://github.com/bincrafters/conan-xkbcommon"
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
        "shared": True,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": False,
        "docs": False,
        "libxcb:shared": True
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
       # take meson from conan since we need version >= 0.47 for customizing installation 
       # (i.e. set installation prefix) - https://mesonbuild.com/Installing.html
       # meson from official ubuntu repos now has version 0.45.1
        if not tools.which("meson"):
            self.build_requires("meson/0.53.2")
       # take next dependencies from the system	
       # if not tools.which("bison"):
       #     self.build_requires("bison_installer/3.4.1)
       # if not tools.which("pkg-config"):
       #     self.build_requires("pkg-config_installer/0.29.2")

    def requirements(self):
        self.requires("xkeyboard-config/2.28")
        if self.options.with_x11:
            self.requires("libxcb/1.13.1")

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
        def _get_pc_files(package):
            if package in self.deps_cpp_info.deps:
                lib_path = self.deps_cpp_info[package].rootpath
                for dirpath, _, filenames in os.walk(lib_path):
                    for filename in filenames:
                        if filename.endswith('.pc'):
                            shutil.copyfile(os.path.join(dirpath, filename), filename)
                            tools.replace_prefix_in_pc_file(filename, lib_path)
                for dep in self.deps_cpp_info[package].public_deps:
                    _get_pc_files(dep)
        _get_pc_files('libxcb')
        _get_pc_files('xkeyboard-config')
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()

    def package_info(self):
        self.env_info.destdir.append("../install")
        self.cpp_info.libs = tools.collect_libs(self)
