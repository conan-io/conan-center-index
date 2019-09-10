#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "http://github.com/bincrafters/conan-libjpeg"
    license = "http://ijg.org/files/README"
    homepage = "http://ijg.org"
    exports = ["LICENSE.md"]
    exports_sources = ["Win32.Mak"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            raise ConanInvalidConfiguration("shared builds aren't supported for MSVC")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("jpeg-" + self.version, self.source_subfolder)

    def build_nmake(self):
        if self.settings.compiler == 'Visual Studio':
            shutil.copy('Win32.Mak', os.path.join(self.source_subfolder, 'Win32.Mak'))
        with tools.chdir(self.source_subfolder):
            shutil.copy('jconfig.vc', 'jconfig.h')
            vcvars_command = tools.vcvars_command(self.settings)
            params = "nodebug=1" if self.settings.build_type == 'Release' else ""
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if self.settings.compiler.runtime in ["MD", "MDd"]:
                tools.replace_in_file('makefile.vc', '(cvars)', '(cvarsdll)')
                tools.replace_in_file('makefile.vc', '(conlibs)', '(conlibsdll)')
            else:
                tools.replace_in_file('makefile.vc', '(cvars)', '(cvarsmt)')
                tools.replace_in_file('makefile.vc', '(conlibs)', '(conlibsmt)')
            self.run('%s && nmake -f makefile.vc %s libjpeg.lib' % (vcvars_command, params))

    def build_configure(self):
        # works for unix and mingw environments
        env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os == 'Windows')
        env_build.fpic = True
        config_args = []
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])
        prefix = os.path.abspath(self.package_folder)
        if self.settings.os == 'Windows':
            prefix = tools.unix_path(prefix)
        config_args.append("--prefix=%s" % prefix)

        # mingw-specific
        if self.settings.os == 'Windows':
            if self.settings.arch == "x86_64":
                config_args.append('--build=x86_64-w64-mingw32')
                config_args.append('--host=x86_64-w64-mingw32')
            if self.settings.arch == "x86":
                config_args.append('--build=i686-w64-mingw32')
                config_args.append('--host=i686-w64-mingw32')

        env_build.configure(configure_dir=self.source_subfolder, args=config_args)
        env_build.make()
        env_build.install()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_nmake()
        else:
            self.build_configure()

    def package(self):
        self.copy("README", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.compiler == "Visual Studio":
            for filename in ['jpeglib.h', 'jerror.h', 'jconfig.h', 'jmorecfg.h']:
                self.copy(pattern=filename, dst="include", src=self.source_subfolder, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self.source_subfolder, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        # can safely drop bin/ because there are no shared builds
        tools.rmdir(os.path.join(self.package_folder, 'bin'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        la = os.path.join(self.package_folder, 'lib', 'libjpeg.la')
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ['libjpeg']
        else:
            self.cpp_info.libs = ['jpeg']
