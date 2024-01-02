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


required_conan_version = ">=1.57.0"


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
    _build_subfolder = "libintl_build"

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

    @property
    def build_folder(self):
        bf = super().build_folder
        return os.path.join(bf, self._build_subfolder) if self._build_subfolder else bf

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
        if is_msvc(self) or self._is_clang_cl:
            self.build_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        libiconv = self.dependencies["libiconv"]
        libiconv_root = unix_path(self, libiconv.package_folder)
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
            env.define("CC", f"{compile_wrapper} {cc}")
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

            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        # INFO: We do a separated build to avoid generating executable with shared libraries and an linker error produced by textstyle
        # First we build libintl in a separated folder, hornoring the shared option
        # Then we build all executables using static linkage only
        self._build_subfolder = "libintl_build"
        autotools = Autotools(self)
        autotools.configure("gettext-runtime")
        autotools.make()
        self._build_subfolder = "gettext_build"
        mkdir(self, self.build_folder)
        with chdir(self, self.build_folder):
            autotools = Autotools(self)
            autotools.configure(args=["--disable-shared", "--disable-static"])
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
        # INFO: We package only the libintl library and the gettext tools (executables)
        self._build_subfolder = "gettext_build"
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        self._build_subfolder = "libintl_build"
        copy(self, "*gnuintl*.dll", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*gnuintl*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*gnuintl*.a", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*gnuintl*.so*", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*gnuintl*.dylib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*libgnuintl.h", self.build_folder, os.path.join(self.package_folder, "include"), keep_path=False)
        rename(self, os.path.join(self.package_folder, "include", "libgnuintl.h"), os.path.join(self.package_folder, "include", "libintl.h"))
        copy(self, "FindGettext.cmake", src=os.path.join(self.export_sources_folder, "cmake"), dst=os.path.join(self.package_folder, "lib", "cmake"))
        self._fix_msvc_libname()

    def package_info(self):
        aclocal = os.path.join(self.package_folder, "res", "aclocal")
        autopoint = os.path.join(self.package_folder, "bin", "autopoint")
        msgmerge = os.path.join(self.package_folder, "bin", "msgmerge")
        msgfmt = os.path.join(self.package_folder, "bin", "msgfmt")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal)
        self.buildenv_info.define_path("AUTOPOINT", autopoint)
        self.buildenv_info.define_path("MSGMERGE", msgmerge)
        self.buildenv_info.define_path("MSGFMT", msgfmt)

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Intl")
        self.cpp_info.set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.libs = ["gnuintl"]
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "FindGettext.cmake")])

        # TODO: the following can be removed when the recipe supports Conan >= 2.0 only
        self.cpp_info.names["cmake_find_package"] = "Intl"
        self.cpp_info.names["cmake_find_package_multi"] = "Intl"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(unix_path_package_info_legacy(self, aclocal))
        self.env_info.AUTOPOINT = unix_path_package_info_legacy(self, autopoint)
