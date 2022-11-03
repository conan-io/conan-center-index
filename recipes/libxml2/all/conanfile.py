from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.scm import Version
from conan.tools.build import cross_building, build_jobs
from conan.tools.files import copy, get, rename, rm, rmdir, replace_in_file, save, chdir, mkdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path, VCVars
from conans import VisualStudioBuildEnvironment
import os

import itertools
import textwrap

required_conan_version = ">=1.53.0"


class Libxml2Conan(ConanFile):
    name = "libxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = "xml", "parser", "validation"
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
        "docbook": True,    # dropped after 2.10.3
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

    @property
    def _option_names(self):
        return [name for name in self.info.options.keys() if name not in ["shared", "fPIC", "include_utils"]]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_mingw_windows(self):
        return self.settings.compiler == "gcc" and self.settings.os == "Windows" and self._settings_build.os == "Windows"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.10.3":
            del self.options.docbook

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.13")
        if self.options.lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.iconv:
            self.requires("libiconv/1.17")
        if self.options.icu:
            self.requires("icu/71.1")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if not (is_msvc(self) or self._is_mingw_windows):
            if self.options.zlib or self.options.lzma or self.options.icu:
                self.tool_requires("pkgconf/1.9.3")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = VCVars(self)
            tc.generate()
            # TODO: no conan v2 build helper for NMake yet (see https://github.com/conan-io/conan/issues/12188)
            #       Better than nothing: rely on legacy VisualStudioBuildEnvironment to inject CL & LIB env vars
            #       in order to honor build_type & runtime from profile
            env = Environment()
            for var, value in VisualStudioBuildEnvironment(self).vars.items():
                env.define(var, value)
            env.vars(self).save_script("buildenv_nmake")
        elif self._is_mingw_windows:
            pass # nothing to do for mingw?  it calls mingw-make directly
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)

            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-static={yes_no(not self.options.shared)}",
            ])
            for option_name in self._option_names:
                option_value = getattr(self.options, option_name)
                tc.configure_args.append(f"--with-{option_name}={yes_no(option_value)}")

            tc.generate()

            tc = PkgConfigDeps(self)
            tc.generate()

            tc = AutotoolsDeps(self)
            tc.generate()


    def _build_msvc(self):
        with chdir(self, os.path.join(self.source_folder, 'win32')):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            args = [
                "cscript",
                "configure.js",
                "compiler=msvc",
                f"prefix={self.package_folder}",
                f"cruntime=/{msvc_runtime_flag(self)}",
                f"debug={debug}",
                f"static={static}",
            ]

            incdirs = [incdir for dep in self.dependencies.values() for incdir in dep.cpp_info.includedirs]
            libdirs = [libdir for dep in self.dependencies.values() for libdir in dep.cpp_info.libdirs]
            args.append("include=\"{}\"".format(";".join(incdirs)))
            args.append("lib=\"{}\"".format(";".join(libdirs)))

            for name in self._option_names:
                cname = {"mem-debug": "mem_debug",
                         "run-debug": "run_debug",
                         "docbook": "docb"}.get(name, name)
                value = getattr(self.options, name)
                value = "yes" if value else "no"
                args.append(f"{cname}={value}")

            configure_command = ' '.join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # Fix library names because they can be not just zlib.lib
            def fix_library(option, package, old_libname):
                if option:
                    libs = []
                    for lib in itertools.chain(self.dependencies[package].cpp_info.libs, self.dependencies[package].cpp_info.system_libs):
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    replace_in_file(self, "Makefile.msvc",
                                          f"LIBS = $(LIBS) {old_libname}",
                                          f"LIBS = $(LIBS) {' '.join(libs)}")

            fix_library(self.options.zlib, 'zlib', 'zlib.lib')
            fix_library(self.options.lzma, "xz_utils", "liblzma.lib")
            fix_library(self.options.iconv, 'libiconv', 'iconv.lib')
            fix_library(self.options.icu, 'icu', 'advapi32.lib sicuuc.lib sicuin.lib sicudt.lib')
            fix_library(self.options.icu, 'icu', 'icuuc.lib icuin.lib icudt.lib')

            self.run("nmake /f Makefile.msvc libxml libxmla libxmladll")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc utils")

    def _package_msvc(self):
        with chdir(self, os.path.join(self.source_folder, 'win32')):
            self.run("nmake /f Makefile.msvc install-libs")

            if self.options.include_utils:
                self.run("nmake /f Makefile.msvc install-dist")


    def _build_mingw(self):
        with chdir(self, os.path.join(self.source_folder, "win32")):
            # configuration
            yes_no = lambda v: "yes" if v else "no"
            args = [
                "cscript",
                "configure.js",
                "compiler=mingw",
                f"prefix={self.package_folder}",
                f"debug={yes_no(self.settings.build_type == 'Debug')}",
                f"static={yes_no(not self.options.shared)}",
            ]

            incdirs = [incdir for dep in self.dependencies.values() for incdir in dep.cpp_info.includedirs]
            libdirs = [libdir for dep in self.dependencies.values() for libdir in dep.cpp_info.libdirs]
            args.append("include=\"{' -I'.join(incdirs)}\"")
            args.append("lib=\"{' -L'.join(libdirs)}\"")

            for name in self._option_names:
                cname = {
                    "mem-debug": "mem_debug",
                    "run-debug": "run_debug",
                    "docbook": "docb",
                }.get(name, name)
                args.append(f"{cname}={yes_no(getattr(self.options, name))}")
            configure_command = " ".join(args)
            self.output.info(configure_command)
            self.run(configure_command)

            # build
            def fix_library(option, package, old_libname):
                if option:
                    replace_in_file(self,
                        "Makefile.mingw",
                        "LIBS += -l{old_libname}",
                        "LIBS += -l{' -l'.join(self.dependencies[package].cpp_info.libs)}",
                    )

            fix_library(self.options.iconv, "libiconv", "iconv")
            fix_library(self.options.zlib, "zlib", "z")
            fix_library(self.options.lzma, "xz_utils", "lzma")

            self.run(f"mingw32-make -j{build_jobs(self)} -f Makefile.mingw libxml libxmla")
            if self.options.include_utils:
                self.run(f"mingw32-make -j{build_jobs(self)} -f Makefile.mingw utils")

    def _package_mingw(self):
        with chdir(self, os.path.join(self.source_folder, "win32")):
            mkdir(self, os.path.join(self.package_folder, "include", "libxml2"))
            self.run("mingw32-make -f Makefile.mingw install-libs")
            if self.options.include_utils:
                self.run("mingw32-make -f Makefile.mingw install-dist")


    def _patch_sources(self):
        # Break dependency of install on build
        for makefile in ("Makefile.mingw", "Makefile.msvc"):
            replace_in_file(self, os.path.join(self.source_folder, "win32", makefile),
                                               "install-libs : all",
                                               "install-libs :")
        # relocatable shared lib on macOS
        replace_in_file(self, os.path.join(self.source_folder, "configure"),
                              "-install_name \\$rpath/",
                              "-install_name @rpath/")


    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        elif self._is_mingw_windows:
            self._build_mingw()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make("libxml2.la")

            if self.options.include_utils:
                for target in ["xmllint", "xmlcatalog", "xml2-config"]:
                    autotools.make(target)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        copy(self, "Copyright", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        if is_msvc(self):
            self._package_msvc()
            # remove redundant libraries to avoid confusion
            if not self.options.shared:
                rm(self, "libxml2.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "libxml2_a_dll.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "libxml2_a.lib" if self.options.shared else "libxml2.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        elif self._is_mingw_windows:
            self._package_mingw()
            if self.options.shared:
                rm(self, "libxml2.a", os.path.join(self.package_folder, "lib"))
                rename(self, os.path.join(self.package_folder, "lib", "libxml2.lib"),
                             os.path.join(self.package_folder, "lib", "libxml2.dll.a"))
            else:
                rm(self, "libxml2.dll", os.path.join(self.package_folder, "bin"))
                rm(self, "libxml2.lib", os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)

            for target in ["install-libLTLIBRARIES", "install-data"]:
                autotools.make(target=target, args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

            if self.options.include_utils:
                autotools.install()

            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rm(self, "*.sh", os.path.join(self.package_folder, "lib"))
            rm(self, "run*", os.path.join(self.package_folder, "bin"))
            rm(self, "test*", os.path.join(self.package_folder, "bin"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        for header in ["win32config.h", "wsockcompat.h"]:
            copy(self, pattern=header, src=os.path.join(self.source_folder, "include"),
                      dst=os.path.join(self.package_folder, "include", "libxml2"), keep_path=False)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
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
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        # FIXME: Provide LibXml2::xmllint & LibXml2::xmlcatalog imported target for executables
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "LibXml2")
        self.cpp_info.set_property("cmake_file_name", "libxml2")
        self.cpp_info.set_property("cmake_target_name", "LibXml2::LibXml2")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "libxml-2.0")
        prefix = "lib" if is_msvc(self) else ""
        suffix = "_a" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}xml2{suffix}"]
        self.cpp_info.includedirs.append(os.path.join("include", "libxml2"))
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
        if self.options.include_utils:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threads and self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("dl")
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
