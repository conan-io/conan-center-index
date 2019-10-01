#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = "XML", "parser", "validation"
    homepage = "https://xmlsoft.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "zlib": [True, False],
               "lzma": [True, False],
               "iconv": [True, False],
               "icu": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       "iconv": True,
                       "zlib": True,
                       "lzma": False,
                       "icu": False}
    _source_subfolder = "source_subfolder"

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.lzma:
            self.requires("xz_utils/5.2.4")
        if self.options.iconv:
            self.requires("libiconv/1.15")
        if self.options.icu:
            self.requires("icu/64.2")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'
    
    @property
    def _is_mingw(self):
        return self.settings.compiler == 'gcc' and self.settings.os == 'Windows'

    @property
    def _full_source_subfolder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libxml2-{0}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        if self._is_msvc:
            self._build_windows()
        elif self._is_mingw:
            self._build_mingw()
        else:
            self._build_with_configure()

    def _build_windows(self):
        with tools.chdir(os.path.join(self._full_source_subfolder, 'win32')):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            with tools.vcvars(self.settings):
                args = ["cscript",
                        "configure.js",
                        "zlib=%d" % (1 if self.options.zlib else 0),
                        "lzma=%d" % (1 if self.options.lzma else 0),
                        "iconv=%d" % (1 if self.options.iconv else 0),
                        "icu=%d" % (1 if self.options.icu else 0),
                        "compiler=msvc",
                        "prefix=%s" % self.package_folder,
                        "cruntime=/%s" % self.settings.compiler.runtime,
                        "debug=%s" % debug,
                        "static=%s" % static,
                        'include="%s"' % ";".join(self.deps_cpp_info.include_paths),
                        'lib="%s"' % ";".join(self.deps_cpp_info.lib_paths)]
                configure_command = ' '.join(args)
                self.output.info(configure_command)
                self.run(configure_command)

                # Fix library names because they can be not just zlib.lib
                def fix_library(option, package, old_libname):
                    if option:
                        libs = []
                        for lib in self.deps_cpp_info[package].libs:
                            libname = lib
                            if not libname.endswith('.lib'):
                                libname += '.lib'
                            libs.append(libname)
                        tools.replace_in_file("Makefile.msvc",
                                              "LIBS = $(LIBS) %s" % old_libname,
                                              "LIBS = $(LIBS) %s" % ' '.join(libs))

                fix_library(self.options.zlib, 'zlib', 'zlib.lib')
                fix_library(self.options.lzma, 'lzma', 'liblzma.lib')
                fix_library(self.options.iconv, 'libiconv', 'iconv.lib')
                fix_library(self.options.icu, 'icu', 'advapi32.lib sicuuc.lib sicuin.lib sicudt.lib')
                fix_library(self.options.icu, 'icu', 'icuuc.lib icuin.lib icudt.lib')

                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake /f Makefile.msvc install")

    def _build_mingw(self):
        with tools.chdir(os.path.join(self._full_source_subfolder, 'win32')):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            args = ["cscript",
                    "configure.js",
                    "zlib=%d" % (1 if self.options.zlib else 0),
                    "lzma=%d" % (1 if self.options.lzma else 0),
                    "iconv=%d" % (1 if self.options.iconv else 0),
                    "icu=%d" % (1 if self.options.icu else 0),
                    "compiler=mingw",
                    "prefix=%s" % self.package_folder,
                    "debug=%s" % debug,
                    "static=%s" % static,
                    'include="%s"' % " -I".join(self.deps_cpp_info.include_paths),
                    'lib="%s"' % " -L".join(self.deps_cpp_info.lib_paths)]
            configure_command = ' '.join(args)
            self.output.info(configure_command)
            self.run(configure_command)
            self.run("mingw32-make -f Makefile.mingw install")

    def _build_with_configure(self):
        in_win = self.settings.os == "Windows"
        env_build = AutoToolsBuildEnvironment(self, win_bash=in_win)
        if not in_win:
            env_build.fpic = self.options.fPIC
        full_install_subfolder = tools.unix_path(self.package_folder) if in_win else self.package_folder
        # fix rpath
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._full_source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        configure_args = ['--with-python=no', '--prefix=%s' % full_install_subfolder]
        if env_build.fpic:
            configure_args.extend(['--with-pic'])
        if self.options.shared:
            configure_args.extend(['--enable-shared', '--disable-static'])
        else:
            configure_args.extend(['--enable-static', '--disable-shared'])
        configure_args.extend(['--with-zlib' if self.options.zlib else '--without-zlib'])
        configure_args.extend(['--with-lzma' if self.options.lzma else '--without-lzma'])
        configure_args.extend(['--with-iconv' if self.options.iconv else '--without-iconv'])
        configure_args.extend(['--with-icu' if self.options.icu else '--without-icu'])

        # Disable --build when building for iPhoneSimulator. The configure script halts on
        # not knowing if it should cross-compile.
        build = None
        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            build = False

        env_build.configure(args=configure_args, build=build, configure_dir=self._full_source_subfolder)
        env_build.make(args=["install"])

    def package(self):
        # copy package license
        self.copy("COPYING", src=self._full_source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.os == "Windows":
            # There is no way to avoid building the tests, but at least we don't want them in the package
            for prefix in ["run", "test"]:
                for test in glob.glob("%s/bin/%s*" % (self.package_folder, prefix)):
                    os.remove(test)
        for header in ["win32config.h", "wsockcompat.h"]:
            self.copy(pattern=header, src=os.path.join(self._full_source_subfolder, "include"),
                      dst=os.path.join("include", "libxml2"), keep_path=False)
        if self._is_msvc:
            # remove redundant libraries to avoid confusion
            os.unlink(os.path.join(self.package_folder, 'lib', 'libxml2_a_dll.lib'))
            os.unlink(os.path.join(self.package_folder, 'lib', 'libxml2_a.lib' if self.options.shared else 'libxml2.lib'))

            pdb_files = glob.glob(os.path.join(self.package_folder, 'bin', '*.pdb'), recursive=True)
            for pdb in pdb_files:
                os.unlink(pdb)

        la = os.path.join(self.package_folder, 'lib', 'libxml2.la')
        if os.path.isfile(la):
            os.unlink(la)

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libxml2' if self.options.shared else 'libxml2_a']
        else:
            self.cpp_info.libs = ['xml2']
        self.cpp_info.includedirs = [os.path.join("include", "libxml2")]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs.append('m')
        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
