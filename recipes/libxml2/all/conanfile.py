from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from contextlib import contextmanager
import glob
import os


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = ("XML", "parser", "validation")
    homepage = "https://xmlsoft.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    generators = "pkg_config"

    # from ./configure and ./win32/configure.js
    default_options = {"shared": False,
                       "fPIC": True,
                       "include_utils": True,
                       "c14n": True,
                       "catalog": True,
                       "docbook": True,
                       "ftp": True,
                       "http": True,
                       "html": True,
                       "iconv": True,
                       "icu": False,
                       "iso8859x": True,
                       "legacy": True,
                       "mem-debug": False,
                       "output": True,
                       "pattern": True,
                       "push": True,
                       "python": False,
                       "reader": True,
                       "regexps": True,
                       "run-debug": False,
                       "sax1": True,
                       "schemas": True,
                       "schematron": True,
                       "threads": True,
                       "tree": True,
                       "valid": True,
                       "writer": True,
                       "xinclude": True,
                       "xpath": True,
                       "xptr": True,
                       "zlib": True,
                       "lzma": False,
                       }

    options = {name: [True, False] for name in default_options.keys()}
    _option_names = [name for name in default_options.keys() if name not in ["shared", "fPIC", "include_utils"]]

    _autotools = None
    _source_subfolder = "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw(self):
        return self.settings.compiler == "gcc" and self.settings.os == "Windows"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.lzma:
            self.requires("xz_utils/5.2.4")
        if self.options.iconv:
            self.requires("libiconv/1.16")
        if self.options.icu:
            self.requires("icu/67.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libxml2-{0}".format(self.version), self._source_subfolder)

    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_msvc(self):
        with self._msvc_build_environment():
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            args = ["cscript",
                    "configure.js",
                    "compiler=msvc",
                    "prefix=%s" % self.package_folder,
                    "cruntime=/%s" % self.settings.compiler.runtime,
                    "debug=%s" % debug,
                    "static=%s" % static,
                    "include='%s'" % ";".join(self.deps_cpp_info.include_paths),
                    "lib='%s'" % ";".join(self.deps_cpp_info.lib_paths)]

            for name in self._option_names:
                cname = {"mem-debug": "mem_debug",
                         "run-debug": "run_debug",
                         "docbook": "docb"}.get(name, name)
                value = getattr(self.options, name)
                value = "yes" if value else "no"
                args.append("%s=%s" % (cname, value))

            configure_command = " ".join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # Fix library names because they can be not just zlib.lib
            def fix_library(option, package, old_libname):
                if option:
                    libs = []
                    for lib in self.deps_cpp_info[package].libs:
                        libname = lib
                        if not libname.endswith(".lib"):
                            libname += ".lib"
                        libs.append(libname)
                    tools.replace_in_file("Makefile.msvc",
                                          "LIBS = $(LIBS) %s" % old_libname,
                                          "LIBS = $(LIBS) %s" % " ".join(libs))

            fix_library(self.options.zlib, "zlib", "zlib.lib")
            fix_library(self.options.lzma, "lzma", "liblzma.lib")
            fix_library(self.options.iconv, "libiconv", "iconv.lib")
            fix_library(self.options.icu, "icu", "advapi32.lib sicuuc.lib sicuin.lib sicudt.lib")
            fix_library(self.options.icu, "icu", "icuuc.lib icuin.lib icudt.lib")

            self.run("nmake /f Makefile.msvc libxml libxmla libxmladll")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc utils")

    def _package_msvc(self):
        with self._msvc_build_environment():
            self.run("nmake /f Makefile.msvc install-libs")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc install-dist")

    def _build_mingw(self):
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            args = [
                "cscript",
                "configure.js",
                "compiler=mingw",
                'prefix="{}"'.format(self.package_folder),
                "debug={}".format(debug),
                "static={}".format(static),
                'include="{}"'.format(" -I".join(self.deps_cpp_info.include_paths)),
                'lib="{}"'.format(" -L".join(self.deps_cpp_info.lib_paths))
            ]

            for name in self._option_names:
                cname = {"mem-debug": "mem_debug",
                         "run-debug": "run_debug",
                         "docbook": "docb"}.get(name, name)
                value = getattr(self.options, name)
                value = "yes" if value else "no"
                args.append("%s=%s" % (cname, value))

            configure_command = " ".join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            self.run("mingw32-make -f Makefile.mingw libxml libxmla")

            if self.options.include_utils:
                self.run("mingw32-make -f Makefile.mingw utils")

    def _package_mingw(self):
        tools.mkdir(os.path.join(self.package_folder, "include", "libxml2"))
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            self.run("mingw32-make -f Makefile.mingw install-libs")

            if self.options.include_utils:
                self.run("mingw32-make -f Makefile.mingw install-dist")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        full_install_subfolder = tools.unix_path(self.package_folder) if tools.os_info.is_windows else self.package_folder
        # fix rpath
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        configure_args = ["--prefix=%s" % full_install_subfolder]
        if self._autotools.fpic:
            configure_args.extend(["--with-pic"])
        if self.options.shared:
            configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            configure_args.extend(["--enable-static", "--disable-shared"])

        for name in self._option_names:
            value = getattr(self.options, name)
            value = ("--with-%s" % name) if value else ("--without-%s" % name)
            configure_args.append(value)

        # Disable --build when building for iPhoneSimulator. The configure script halts on
        # not knowing if it should cross-compile.
        build = None
        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            build = False

        self._autotools.configure(args=configure_args, build=build, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Break dependency of install on build
        for makefile in ("Makefile.mingw", "Makefile.msvc"):
            tools.replace_in_file(os.path.join(self._source_subfolder, "win32", makefile),
                                               "install-libs : all",
                                               "install-libs :")

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        elif self._is_mingw:
            self._build_mingw()
        else:
            autotools = self._configure_autotools()
            autotools.make(["libxml2.la"])

            if self.options.include_utils:
                ext = ".exe" if self.settings.os == "Windows" else ""
                autotools.make(["xmllint" + ext, "xmlcatalog" + ext, "xml2-config"])

    def package(self):
        # copy package license
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self._is_msvc:
            self._package_msvc()
            # remove redundant libraries to avoid confusion
            if not self.options.shared:
                os.remove(os.path.join(self.package_folder, "bin", "libxml2.dll"))
            os.remove(os.path.join(self.package_folder, "lib", "libxml2_a_dll.lib"))
            os.remove(os.path.join(self.package_folder, "lib", "libxml2_a.lib" if self.options.shared else "libxml2.lib"))
            for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.remove(pdb_file)
        elif self._is_mingw:
            self._package_mingw()
            if self.options.shared:
                os.remove(os.path.join(self.package_folder, "lib", "libxml2.a"))
                os.rename(os.path.join(self.package_folder, "lib", "libxml2.lib"),
                          os.path.join(self.package_folder, "lib", "libxml2.a"))
            else:
                os.remove(os.path.join(self.package_folder, "bin", "libxml2.dll"))
                os.remove(os.path.join(self.package_folder, "lib", "libxml2.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.make(["install-libLTLIBRARIES", "install-data"])

            if self.options.include_utils:
                ext = ".exe" if self.settings.os == "Windows" else ""
                autotools.make(["xmllint" + ext, "xmlcatalog" + ext, "xml2-config"])

            os.remove(os.path.join(self.package_folder, "lib", "libxml2.la"))
            for prefix in ["run", "test"]:
                for test in glob.glob(os.path.join(self.package_folder, "bin", prefix + "*")):
                    os.remove(test)
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        for header in ["win32config.h", "wsockcompat.h"]:
            self.copy(pattern=header, src=os.path.join(self._source_subfolder, "include"),
                      dst=os.path.join("include", "libxml2"), keep_path=False)

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.components["xml2lib"].libs = ["libxml2" if self.options.shared else "libxml2_a"]
        else:
            self.cpp_info.components["xml2lib"].libs = ["xml2"]
        self.cpp_info.components["xml2lib"].includedirs.append(os.path.join("include", "libxml2"))
        if not self.options.shared:
            self.cpp_info.components["xml2lib"].defines = ["LIBXML_STATIC"]

        if self.settings.os == "Linux":
            self.cpp_info.components["xml2lib"].system_libs.append("m")
        if self.settings.os == "Windows":
            self.cpp_info.components["xml2lib"].system_libs.append("ws2_32")
        if self.options.threads:
            if self.settings.os == "Linux":
                self.cpp_info.components["xml2lib"].system_libs.append("pthread")

        if self.options.zlib:
            self.cpp_info.components["xml2lib"].requires.append("zlib::zlib")
        if self.options.lzma:
            self.cpp_info.components["xml2lib"].requires.append("xz_utils::xz_utils")
        if self.options.iconv:
            self.cpp_info.components["xml2lib"].requires.append("libiconv::libiconv")
        if self.options.icu:
            self.cpp_info.components["xml2lib"].requires.append("icu::icu")

        self.cpp_info.components["xml2lib"].names["pkg_config"] = "libxml-2.0"
        self.cpp_info.filenames["cmake_find_package"] = "LibXml2"
        self.cpp_info.filenames["cmake_find_package_multi"] = "LibXml2"
        self.cpp_info.names["cmake_find_package"] = "LibXml2"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXml2"
        self.cpp_info.components["xml2lib"].names["cmake_find_package"] = "LibXml2"
        self.cpp_info.components["xml2lib"].names["cmake_find_package_multi"] = "LibXml2"

        # FIXME: libxml2 package itself creates libxml2-config.cmake file

        if self.options.include_utils:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
#             FIXME: cmake creates LibXml2::xmllint imported target for the xmllint executable
