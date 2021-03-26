from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from contextlib import contextmanager
import glob
import os
import textwrap

required_conan_version = ">=1.29.1"


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = ("XML", "parser", "validation")
    homepage = "https://xmlsoft.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    # from ./configure and ./win32/configure.js
    default_options = {
        "shared": False,
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

    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
            self.requires("xz_utils/5.2.5")
        if self.options.iconv:
            self.requires("libiconv/1.16")
        if self.options.icu:
            self.requires("icu/68.2")

    def build_requirements(self):
        if not self._is_msvc:
            if self.options.zlib or self.options.lzma or self.options.icu:
                self.build_requires("pkgconf/1.7.3")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libxml2-{0}".format(self.version), self._source_subfolder)

    @contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(os.path.join(self._source_subfolder, 'win32')):
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
                    'include="%s"' % ";".join(self.deps_cpp_info.include_paths),
                    'lib="%s"' % ";".join(self.deps_cpp_info.lib_paths)]

            for name in self._option_names:
                cname = {"mem-debug": "mem_debug",
                         "run-debug": "run_debug",
                         "docbook": "docb"}.get(name, name)
                value = getattr(self.options, name)
                value = "yes" if value else "no"
                args.append("%s=%s" % (cname, value))

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

            self.run("nmake /f Makefile.msvc libxml libxmla libxmladll")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc utils")


    def _package_msvc(self):
        with self._msvc_build_environment():
            self.run("nmake /f Makefile.msvc install-libs")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc install-dist")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        full_install_subfolder = tools.unix_path(self.package_folder) if tools.os_info.is_windows else self.package_folder
        configure_args = ['--prefix=%s' % full_install_subfolder]
        configure_args.append("--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic")
        if self.options.shared:
            configure_args.extend(['--enable-shared', '--disable-static'])
        else:
            configure_args.extend(['--enable-static', '--disable-shared'])

        for name in self._option_names:
            value = getattr(self.options, name)
            value = ("--with-%s" % name) if value else ("--without-%s" % name)
            configure_args.append(value)

        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        # Break dependency of install on build
        for makefile in ("Makefile.mingw", "Makefile.msvc"):
            tools.replace_in_file(os.path.join(self._source_subfolder, "win32", makefile),
                                               "install-libs : all",
                                               "install-libs :")
        # fix rpath
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make(["libxml2.la"])

            if self.options.include_utils:
                autotools.make(["xmllint", "xmlcatalog", "xml2-config"])

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
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        else:
            autotools = self._configure_autotools()
            autotools.make(["install-libLTLIBRARIES", "install-data"])

            if self.options.include_utils:
                autotools.make(["install", "xmllint", "xmlcatalog", "xml2-config"])

            os.remove(os.path.join(self.package_folder, "lib", "libxml2.la"))
            for prefix in ["run", "test"]:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), prefix + "*")
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        for header in ["win32config.h", "wsockcompat.h"]:
            self.copy(pattern=header, src=os.path.join(self._source_subfolder, "include"),
                      dst=os.path.join("include", "libxml2"), keep_path=False)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        # FIXME: also define LIBXML2_XMLLINT_EXECUTABLE variable
        content = textwrap.dedent("""\
            if(DEFINED LibXml2_FOUND)
                set(LIBXML2_FOUND ${LibXml2_FOUND})
            endif()
            if(DEFINED LibXml2_INCLUDE_DIR)
                set(LIBXML2_INCLUDE_DIR ${LibXml2_INCLUDE_DIR})
                set(LIBXML2_INCLUDE_DIRS ${LibXml2_INCLUDE_DIR})
            endif()
            if(DEFINED LibXml2_LIBRARIES)
                set(LIBXML2_LIBRARIES ${LibXml2_LIBRARIES})
                set(LIBXML2_LIBRARY ${LibXml2_LIBRARIES})
            endif()
            if(DEFINED LibXml2_DEFINITIONS)
                set(LIBXML2_DEFINITIONS ${LibXml2_DEFINITIONS})
            endif()
            if(DEFINED LibXml2_VERSION)
                set(LIBXML2_VERSION_STRING ${LibXml2_VERSION})
            endif()
        """)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-variables.cmake".format(self.name)

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libxml2' if self.options.shared else 'libxml2_a']
        else:
            self.cpp_info.libs = ['xml2']
        self.cpp_info.includedirs.append(os.path.join("include", "libxml2"))
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
        if self.options.include_utils:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threads and self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            if self.options.ftp or self.options.http:
                self.cpp_info.system_libs.extend(["ws2_32", "wsock32"])
        # FIXME: cmake creates LibXml2::xmllint imported target for the xmllint executable
        self.cpp_info.names["cmake_find_package"] = "LibXml2"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXml2"
        self.cpp_info.names["pkg_config"] = "libxml-2.0"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules = [os.path.join(self._module_subfolder, self._module_file)]
