import os
import glob

from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, chdir, rm, rename, mkdir
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, unix_path_package_info_legacy
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conan.tools.build import cross_building


required_conan_version = ">=2.1.0"


class GetTextConan(ConanFile):
    name = "gettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = ("GPL-3.0-or-later", "LGPL-2.1-or-later")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": ["posix", "solaris", "pth", "windows", "disabled"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": "posix",
    }

    @property
    def _gettext_tools_folder(self):
        return "gettext-tools"

    @property
    def _gettext_runtime_folder(self):
        return "gettext-runtime"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
               self.settings.compiler.get_safe("runtime")

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/FindGettext.cmake", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if str(self.settings.os) in ["Windows", "Solaris"]:
            self.options.threads = str(self.settings.os).lower()

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self.version >= Version("0.22") or is_msvc(self) or self._is_clang_cl:
            self.build_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        libiconv = self.dependencies["libiconv"]
        libiconv_root = unix_path(self, libiconv.package_folder)

        tc = AutotoolsToolchain(self, namespace="libintl")
        tc.configure_args.extend([
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--datarootdir=${prefix}/res",
            f"--with-libiconv-prefix={libiconv_root}",
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-openmp",
            "--disable-curses",
            "--disable-threads" if self.options.threads == "disabled" else ("--enable-threads=" + str(self.options.threads)),
            "--with-included-glib",
            "--with-included-libxml",
            "--with-included-libunistring",
            "--with-installed-libtextstyle=no",
            "--without-cvs",
            "--without-emacs",
            "--without-git",
            "--without-libcurses-prefix",
            "--without-libncurses-prefix",
            "--without-libtermcap-prefix",
            "--without-libxcurses-prefix",
            "--without-included-gettext",
        ])

        env = tc.environment()
        if is_msvc(self) or self._is_clang_cl:
            def programs():
                rc = None
                if self.settings.arch == "x86_64":
                    rc = "windres --target=pe-x86-64"
                elif self.settings.arch == "x86":
                    rc = "windres --target=pe-i386"
                if self._is_clang_cl:
                    compiler = self.conf.get("tools.build:compiler_executable", check_type=str) or "clang-cl"
                    return compiler, os.getenv("AR", "llvm-lib"), os.getenv("LD", "lld-link"), rc
                if is_msvc(self):
                    return "cl -nologo", "lib", "link", rc

            target = None
            if self.settings.arch == "x86_64":
                target = "x86_64-w64-mingw32"
            elif self.settings.arch == "x86":
                target = "i686-w64-mingw32"
            if target is not None:
                tc.configure_args += [f"--host={target}", f"--build={target}"]

            if check_min_vs(self, "180", raise_invalid=False):
                # INFO: https://github.com/conan-io/conan/issues/15365
                tc.extra_cflags.append("-FS")

            # prevent redefining compiler instrinsic functions
            tc.configure_args.extend([
                'ac_cv_func_memmove=yes',
                'ac_cv_func_memset=yes'
            ])

            # Skip checking for the 'n' printf format directly
            # in msvc, as it is known to not be available due to security concerns.
            # Skipping it avoids a GUI prompt during ./configure for a debug build
            # See https://github.com/conan-io/conan-center-index/issues/23698]
            if self.settings.build_type == "Debug":
                tc.configure_args.extend(['gl_cv_func_printf_directive_n=no'])

            # The flag above `--with-libiconv-prefix` fails to correctly detect libiconv on windows+msvc
            # so it needs an extra nudge. We could use `AutotoolsDeps` but it's currently affected by the
            # following outstanding issue: https://github.com/conan-io/conan/issues/12784
            #iconv_includedir = unix_path(self, libiconv.cpp_info.aggregated_components().includedirs[0])
            #iconv_libdir = unix_path(self, libiconv.cpp_info.aggregated_components().libdirs[0])
            #tc.extra_cflags.append(f"-I{iconv_includedir}")
            #tc.extra_ldflags.append(f"-L{iconv_libdir}")

            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            compile_wrapper = unix_path(self, self.dependencies.build["automake"].conf_info.get("user.automake:compile-wrapper"))
            ar_wrapper = unix_path(self, self.dependencies.build["automake"].conf_info.get("user.automake:lib-wrapper"))
            cc, ar, link, rc = programs()
            env.define("CC", "{} cl -nologo".format(unix_path(self, compile_wrapper)))
            env.define("CXX", f"{compile_wrapper} {cc}")
            env.define("LD", link)
            env.define("AR", f"{ar_wrapper} {ar}")
            env.define("NM", "dumpbin -symbols")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            if rc is not None:
                env.define("RC", rc)
                env.define("WINDRES", rc)
        tc.generate(env)

        tc = AutotoolsToolchain(self, namespace="gettext-tools")
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
            f"--with-libiconv-prefix={libiconv_root}",
            "--disable-dependency-tracking",
            "--disable-shared",
            "--disable-static",
            "--enable-nls",
            # "--disable-nls", # FIXME: msgcmp.c:109:36: error: too few arguments to function 'relocate'
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-curses",
            "--disable-threads",
            "--without-emacs",
            "--without-git",
            "--without-cvs",
            "--without-libcurses-prefix",
            "--without-libncurses-prefix",
            "--without-libtermcap-prefix",
            "--without-libxcurses-prefix",
            "--without-included-gettext",
            "--with-included-glib",
            "--with-included-libxml",
            "--with-included-libunistring",
            "--with-installed-libtextstyle=no",
        ])
        env = tc.environment()
        if is_msvc(self):
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")  # TODO: reference github issue

            # prevent redefining compiler instrinsic functions
            tc.configure_args.extend([
                'ac_cv_func_memmove=yes',
                'ac_cv_func_memset=yes'
            ])

            # Skip checking for the 'n' printf format directly
            # in msvc, as it is known to not be available due to security concerns.
            # Skipping it avoids a GUI prompt during ./configure for a debug build
            # See https://github.com/conan-io/conan-center-index/issues/23698]
            if self.settings.build_type == "Debug":
                tc.configure_args.extend(['gl_cv_func_printf_directive_n=no'])

            # The flag above `--with-libiconv-prefix` fails to correctly detect libiconv on windows+msvc
            # so it needs an extra nudge. We could use `AutotoolsDeps` but it's currently affected by the
            # following outstanding issue: https://github.com/conan-io/conan/issues/12784
            iconv_includedir = unix_path(self, libiconv.cpp_info.aggregated_components().includedirs[0])
            iconv_libdir = unix_path(self, libiconv.cpp_info.aggregated_components().libdirs[0])
            tc.extra_cflags.append(f"-I{iconv_includedir}")
            tc.extra_ldflags.append(f"-L{iconv_libdir}")

            compile_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:compile-wrapper")
            lib_wrapper = self.dependencies.build["automake"].conf_info.get("user.automake:lib-wrapper")
            env.define("CC", "{} cl -nologo".format(unix_path(self, compile_wrapper)))
            env.define("LD", "link -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("STRIP", ":")
            env.define("AR", "{} lib".format(unix_path(self, lib_wrapper)))
            env.define("RANLIB", ":")

            # One of the checks performed by the configure script requires this as a preprocessor flag
            # rather than a C compiler flag
            env.prepend("CPPFLAGS", f"-I{iconv_includedir}")

            windres_arch = {"x86": "i686", "x86_64": "x86-64"}[str(self.settings.arch)]
            env.define("RC", f"windres --target=pe-{windres_arch}")
            env.vars(self).save_script("conanbuild_msvc")
        tc.generate(env)

        if is_msvc(self) or self._is_clang_cl:
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in self.dependencies.values():
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)

            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        # libintl
        mkdir(self, os.path.join(self.build_folder, "libintl_build"))
        with chdir(self, os.path.join(self.build_folder, "libintl_build")):
            autotools = Autotools(self, namespace="libintl")
            autotools.configure("gettext-runtime")
            autotools.make()

        # gettext-runtime
        mkdir(self, os.path.join(self.build_folder, "gettext_build"))
        with chdir(self, os.path.join(self.build_folder, "gettext_build")):
            autotools = Autotools(self, namespace="gettext-tools")
            autotools.configure()
            autotools.make()

    def _fix_msvc_libname(self):
        """Remove lib prefix & change extension to .lib in case of cl like compiler
        """
        if self.settings.get_safe("compiler.runtime"):
            libdirs = getattr(self.cpp.package, "libdirs")
            for libdir in libdirs:
                for ext in [".dll.a", ".dll.lib", ".a"]:
                    full_folder = os.path.join(self.package_folder, libdir)
                    for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                        libname = os.path.basename(filepath)[0:-len(ext)]
                        if libname[0:3] == "lib":
                            libname = libname[3:]
                        rename(self, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, os.path.join(self.build_folder, "libintl_build")):
            autotools = Autotools(self, namespace="libintl")
            autotools.install()

        with chdir(self, os.path.join(self.build_folder, "gettext_build")):
            autotools = Autotools(self, namespace="gettext-tools")
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "res", "doc"))
        rmdir(self, os.path.join(self.package_folder, "res", "info"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))

        # TODO: check about the header name and preserve the original name
        # rename(self, os.path.join(self.package_folder, "include", "libgnuintl.h"), os.path.join(self.package_folder, "include", "libintl.h"))

        copy(self, "FindGettext.cmake", src=os.path.join(self.export_sources_folder, "cmake"), dst=os.path.join(self.package_folder, "lib", "cmake"))
        self._fix_msvc_libname()

    def package_info(self):
        aclocal = os.path.join(self.package_folder, "res", "aclocal")
        autopoint = os.path.join(self.package_folder, "bin", "autopoint")
        msgmerge = os.path.join(self.package_folder, "bin", "msgmerge")
        msgfmt = os.path.join(self.package_folder, "bin", "msgfmt")
        gettext = os.path.join(self.package_folder, "bin", "gettext")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal)
        self.buildenv_info.define_path("AUTOPOINT", autopoint)
        self.buildenv_info.define_path("MSGMERGE", msgmerge)
        self.buildenv_info.define_path("MSGFMT", msgfmt)
        self.buildenv_info.define_path("GETTEXT", gettext)

        self.cpp_info.components["intl"].set_property("cmake_find_mode", "both")
        self.cpp_info.components["intl"].set_property("cmake_file_name", "Intl")
        self.cpp_info.components["intl"].set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.components["intl"].libs = ["gnuintl"]
        if is_apple_os(self):
            self.cpp_info.components["intl"].frameworks.append("CoreFoundation")

        self.cpp_info.components["intl"].builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.components["intl"].set_property("cmake_build_modules", [os.path.join("lib", "cmake", "FindGettext.cmake")])
