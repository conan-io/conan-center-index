from conans import Meson, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.45.0"

class LibGlvndConan(ConanFile):
    name = "libglvnd"
    description = "The GL Vendor-Neutral Dispatch library"
    license = "custom"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/glvnd/libglvnde"
    topics = ("gl", "vendor-neutral", "dispatch")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "asm": [True, False],
        "x11": [True, False],
        "egl": [True, False],
        "glx": [True, False],
        "gles1": [True, False],
        "gles2": [True, False],
        "tls": [True, False],
        "dispatch_tls": [True, False],
        "headers": [True, False],
        "entrypoint_patching": [True, False],
    }
    default_options = {
        "asm" : True,
        "x11": True,
        "egl": True,
        "glx": True,
        "gles1": True,
        "gles2": True,
        "tls": True,
        "dispatch_tls": True,
        "headers": True,
        "entrypoint_patching": True,
    }

    generators = "pkg_config"


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    # don't use self.settings_build
    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    # don't use self.user_info_build
    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.x11:
            self.requires("xorg/system")
        if self.options.glx:
            self.requires("xorg-proto/2021.4")

    def validate(self):
        if self.settings.os not in ['Linux', 'FreeBSD']:
            raise ConanInvalidConfiguration("libglvnd is only compatible with Linux and FreeBSD")

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs["asm"] = self.options.asm
        defs["x11"] = self.options.x11
        defs["egl"] = self.options.egl
        defs["glx"] = self.options.glx
        defs["gles1"] = self.options.gles1
        defs["gles2"] = self.options.gles2
        defs["tls"] = self.options.tls
        defs["dispatch-tls"] = self.options.dispatch_tls
        defs["headers"] = self.options.headers
        defs["entrypoint-patching"] = self.options.entrypoint_patching
        meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        meson = self._configure_meson()
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), textwrap.dedent('''\
            Copyright (c) 2013, NVIDIA CORPORATION.

            Permission is hereby granted, free of charge, to any person obtaining a
            copy of this software and/or associated documentation files (the
            "Materials"), to deal in the Materials without restriction, including
            without limitation the rights to use, copy, modify, merge, publish,
            distribute, sublicense, and/or sell copies of the Materials, and to
            permit persons to whom the Materials are furnished to do so, subject to
            the following conditions:

            The above copyright notice and this permission notice shall be included
            unaltered in all copies or substantial portions of the Materials.
            Any additions, deletions, or changes to the original source files
            must be clearly indicated in accompanying documentation.

            THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
            EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
            MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
            IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
            CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
            TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
            MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
            '''))

    def package_info(self):
        self.cpp_info.components['gldispatch'].libs = ["GLdispatch"]
        self.cpp_info.components['gldispatch'].system_libs.extend(["pthread", "dl"])

        self.cpp_info.components['opengl'].libs = ["OpenGL"]
        self.cpp_info.components['opengl'].requires.extend(["gldispatch"])
        self.cpp_info.components['opengl'].set_property("pkg_config_name", "opengl")

        if self.options.egl:
            self.cpp_info.components['egl'].libs = ["EGL"]
            self.cpp_info.components['egl'].system_libs.extend(["pthread", "dl", "m"])
            self.cpp_info.components['egl'].requires.extend(["xorg::x11", "gldispatch"])
            self.cpp_info.components['egl'].set_property("pkg_config_name", "egl")

        if self.options.glx:
            self.cpp_info.components['glx'].libs = ["GLX"]
            self.cpp_info.components['glx'].system_libs.extend(["dl"])
            self.cpp_info.components['glx'].requires.extend(["xorg::x11", "xorg-proto::glproto", "gldispatch"])
            self.cpp_info.components['glx'].set_property("pkg_config_name", "glx")

            self.cpp_info.components['gl'].libs = ["GL"]
            self.cpp_info.components['gl'].system_libs.extend(["dl"])
            self.cpp_info.components['gl'].requires.extend(["xorg::x11", "glx", "gldispatch"])
            self.cpp_info.components['gl'].set_property("pkg_config_name", "gl")

        if self.options.gles1:
            self.cpp_info.components['gles1'].libs = ["GLESv1_CM"]
            self.cpp_info.components['gles1'].requires.extend(["gldispatch"])
            self.cpp_info.components['gles1'].set_property("pkg_config_name", "glesv1_cm")
            
        if self.options.gles2:
            self.cpp_info.components['gles2'].libs = ["GLESv2"]
            self.cpp_info.components['gles2'].requires.extend(["gldispatch"])
            self.cpp_info.components['gles2'].set_property("pkg_config_name", "glesv2")
