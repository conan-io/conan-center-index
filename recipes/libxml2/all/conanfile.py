from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from contextlib import contextmanager
from conan.tools.files import rename
import functools
import itertools
import os
import textwrap

required_conan_version = ">=1.43.0"


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = ("xml", "parser", "validation")
    homepage = "https://gitlab.gnome.org/GNOME/libxml2/-/wikis/"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_mingw_windows(self):
        return self.settings.compiler == "gcc" and self.settings.os == "Windows" and self._settings_build.os == "Windows"

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
            self.requires("zlib/1.2.12")
        if self.options.lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.iconv:
            self.requires("libiconv/1.17")
        if self.options.icu:
            self.requires("icu/71.1")

    def build_requirements(self):
        if not (self._is_msvc or self._is_mingw_windows):
            if self.options.zlib or self.options.lzma or self.options.icu:
                self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        # can't use strip_root here because if fails since 2.9.10 with:
        # KeyError: "linkname 'libxml2-2.9.1x/test/relaxng/ambig_name-class.xml' not found"
        tools.files.get(self, **self.conan_data["sources"][self.version])
        rename(self, "libxml2-{}".format(self.version), self._source_subfolder)

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

            args = [
                "cscript",
                "configure.js",
                "compiler=msvc",
                "prefix={}".format(self.package_folder),
                "cruntime=/{}".format(self.settings.compiler.runtime),
                "debug={}".format(debug),
                "static={}".format(static),
            ]
            if self.deps_cpp_info.include_paths:
                args.append("include=\"{}\"".format(";".join(self.deps_cpp_info.include_paths)))
            if self.deps_cpp_info.lib_paths:
                args.append("lib=\"{}\"".format(";".join(self.deps_cpp_info.lib_paths)))

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
                    for lib in itertools.chain(self.deps_cpp_info[package].libs, self.deps_cpp_info[package].system_libs):
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    tools.replace_in_file("Makefile.msvc",
                                          "LIBS = $(LIBS) %s" % old_libname,
                                          "LIBS = $(LIBS) %s" % ' '.join(libs))

            fix_library(self.options.zlib, 'zlib', 'zlib.lib')
            fix_library(self.options.lzma, "xz_utils", "liblzma.lib")
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

    @contextmanager
    def _mingw_build_environment(self):
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            with tools.environment_append(AutoToolsBuildEnvironment(self).vars):
                yield

    def _build_mingw(self):
        with self._mingw_build_environment():
            # configuration
            yes_no = lambda v: "yes" if v else "no"
            args = [
                "cscript",
                "configure.js",
                "compiler=mingw",
                "prefix={}".format(self.package_folder),
                "debug={}".format(yes_no(self.settings.build_type == "Debug")),
                "static={}".format(yes_no(not self.options.shared)),
            ]
            if self.deps_cpp_info.include_paths:
                args.append("include=\"{}\"".format(" -I".join(self.deps_cpp_info.include_paths)))
            if self.deps_cpp_info.lib_paths:
                args.append("lib=\"{}\"".format(" -L".join(self.deps_cpp_info.lib_paths)))

            for name in self._option_names:
                cname = {
                    "mem-debug": "mem_debug",
                    "run-debug": "run_debug",
                    "docbook": "docb",
                }.get(name, name)
                args.append("{}={}".format(cname, yes_no(getattr(self.options, name))))
            configure_command = " ".join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # build
            def fix_library(option, package, old_libname):
                if option:
                    tools.replace_in_file(
                        "Makefile.mingw",
                        "LIBS += -l{}".format(old_libname),
                        "LIBS += -l{}".format(" -l".join(self.deps_cpp_info[package].libs)),
                    )

            fix_library(self.options.iconv, "libiconv", "iconv")
            fix_library(self.options.zlib, "zlib", "z")
            fix_library(self.options.lzma, "xz_utils", "lzma")

            self.run("mingw32-make -j{} -f Makefile.mingw libxml libxmla".format(tools.cpu_count()))
            if self.options.include_utils:
                self.run("mingw32-make -j{} -f Makefile.mingw utils".format(tools.cpu_count()))

    def _package_mingw(self):
        with self._mingw_build_environment():
            tools.mkdir(os.path.join(self.package_folder, "include", "libxml2"))
            self.run("mingw32-make -f Makefile.mingw install-libs")
            if self.options.include_utils:
                self.run("mingw32-make -f Makefile.mingw install-dist")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        for option_name in self._option_names:
            option_value = getattr(self.options, option_name)
            args.append("--with-{}={}".format(option_name, yes_no(option_value)))

        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        # Break dependency of install on build
        for makefile in ("Makefile.mingw", "Makefile.msvc"):
            tools.replace_in_file(os.path.join(self._source_subfolder, "win32", makefile),
                                               "install-libs : all",
                                               "install-libs :")
        # relocatable shared lib on macOS
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                              "-install_name \\$rpath/",
                              "-install_name @rpath/")

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        elif self._is_mingw_windows:
            self._build_mingw()
        else:
            with tools.run_environment(self):   # required for ICU build
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
        elif self._is_mingw_windows:
            self._package_mingw()
            if self.options.shared:
                os.remove(os.path.join(self.package_folder, "lib", "libxml2.a"))
                tools.rename(os.path.join(self.package_folder, "lib", "libxml2.lib"),
                             os.path.join(self.package_folder, "lib", "libxml2.dll.a"))
            else:
                os.remove(os.path.join(self.package_folder, "bin", "libxml2.dll"))
                os.remove(os.path.join(self.package_folder, "lib", "libxml2.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.make(["install-libLTLIBRARIES", "install-data"])

            if self.options.include_utils:
                autotools.make(["install", "xmllint", "xmlcatalog", "xml2-config"])

            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.sh")
            for prefix in ["run", "test"]:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), prefix + "*")
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        for header in ["win32config.h", "wsockcompat.h"]:
            self.copy(pattern=header, src=os.path.join(self._source_subfolder, "include"),
                      dst=os.path.join("include", "libxml2"), keep_path=False)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        # FIXME: Provide LibXml2::xmllint & LibXml2::xmlcatalog imported target for executables
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "LibXml2")
        self.cpp_info.set_property("cmake_file_name", "libxml2")
        self.cpp_info.set_property("cmake_target_name", "LibXml2::LibXml2")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "libxml-2.0")
        prefix = "lib" if self._is_msvc else ""
        suffix = "_a" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["{}xml2{}".format(prefix, suffix)]
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

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "LibXml2"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libxml2"
        self.cpp_info.names["cmake_find_package"] = "LibXml2"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXml2"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "libxml-2.0"
