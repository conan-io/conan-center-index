#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import re

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-community/conan-fontconfig"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    author = "Conan Community"
    topics = ("conan", "fontconfig", "fonts", "freedesktop")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "pkg_config"
    exports = "LICENSE"
    _source_subfolder = "source_subfolder"
    _autotools = None

    def requirements(self):
        self.requires("freetype/2.10.1")
        self.requires("expat/2.2.9")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds are not supported.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        source_url = "https://www.freedesktop.org/software/fontconfig/release/fontconfig-{}.tar.gz"
        sha256 = "19e5b1bc9d013a52063a44e1307629711f0bfef35b9aca16f9c793971e2eb1e5"
        tools.get(source_url.format(self.version), sha256=sha256)
        extrated_dir = self.name + "-" + self.version
        os.rename(extrated_dir, self._source_subfolder)

    def build_requirements(self):
        self.build_requires("gperf/3.1")
        if not tools.which("pkg-config"):
            self.build_requires("pkg-config_installer/0.29.2@bincrafters/stable")

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--enable-static=%s" % ("no" if self.options.shared else "yes"),
                    "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                    "--disable-docs"]
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
            tools.replace_in_file("Makefile", "po-conf test", "po-conf")
        return self._autotools

    def _patch_files(self):
        def rename_if_exists(old, new):
            if os.path.exists(old):
                os.rename(old, new)
        #  - fontconfig requires libtool version number, change it for the corresponding freetype one
        tools.replace_in_file(os.path.join(self._source_subfolder, 'configure'), '21.0.15', '2.8.1')
        rename_if_exists('freetype.pc', 'freetype2.pc')

    def build(self):
        # Patch files from dependencies
        self._patch_files()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        la = os.path.join(self.package_folder, "lib", "libfontconfig.la")
        if os.path.isfile(la):
            os.unlink(la)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["m", "pthread"])
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))
