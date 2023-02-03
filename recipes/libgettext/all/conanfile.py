import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GetTextConan(ConanFile):
    name = "libgettext"
    description = "An internationalization and localization system for multilingual programs"
    topics = ("gettext", "intl", "libintl", "i18n")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": ["posix", "solaris", "pth", "windows", "disabled", "auto"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": "auto",
    }

    @property
    def _is_clang_cl(self):
        return (str(self.settings.compiler) in ["clang"] and str(self.settings.os) in ["Windows"]) or \
               self.settings.get_safe("compiler.toolset") == "ClangCL"

    @property
    def _gettext_folder(self):
        return "gettext-tools"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if (self.options.threads == "auto"):
            self.options.threads = {"Solaris": "solaris", "Windows": "windows"}.get(str(self.settings.os), "posix")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self) or self._is_clang_cl:
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "HELP2MAN=/bin/true",
            "EMACS=no",
            "--disable-nls",
            "--disable-dependency-tracking",
            "--enable-relocatable",
            "--disable-c++",
            "--disable-java",
            "--disable-csharp",
            "--disable-libasprintf",
            "--disable-curses",
            "--disable-threads" if self.options.threads == "disabled" else ("--enable-threads=" + str(self.options.threads)),
            f"--with-libiconv-prefix={unix_path(self, self.deps_cpp_info['libiconv'].rootpath)}"
        ]
        if is_msvc(self) or self._is_clang_cl:
            target = None
            if self.settings.arch == "x86_64":
                target = "x86_64-w64-mingw32"
            elif self.settings.arch == "x86":
                target = "i686-w64-mingw32"

            if target is not None:
                tc.configure_args += [f"--host={target}", f"--build={target}"]

            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
               (self.settings.compiler == "msvc" and Version(self.settings.compiler.version) >= "180"):
                tc.extra_cflags += ["-FS"]

        tc.make_args += ["-C", "intl"]
        tc.generate()

        deps = AutotoolsDeps(self)

        if is_msvc(self) or self._is_clang_cl:
            # This mimics the v1 recipe, on the basis that it works and the defaults do not.
            def lib_paths():
                for dep in self.deps_cpp_info.deps:
                    dep_info = self.deps_cpp_info[dep]
                    for lib_path in dep_info.lib_paths:
                        yield unix_path(self, lib_path)

            fixed_cppflags_args = deps.vars().get("CPPFLAGS").replace("/I", "-I")
            deps.environment.define("CPPFLAGS", f"$CPPFLAGS {fixed_cppflags_args}")
            if self._is_clang_cl:
                fixed_ldflags_args = deps.vars().get("LDFLAGS").replace("/LIBPATH:", "-LIBPATH:")
            else:
                fixed_ldflags_args = deps.vars().get("LDFLAGS").replace("/LIBPATH:", "-L")
            deps.environment.define("LDFLAGS", f"$LDFLAGS {fixed_ldflags_args}")

            libs = deps.vars().get("LIBS")
            deps.environment.define("_LINK_", libs)
            deps.environment.unset("LIBS")

            for lib_path in lib_paths():
                deps.environment.prepend_path("LIB", lib_path)

        deps.generate()

        if is_msvc(self) or self._is_clang_cl:
            def programs():
                rc = None
                if self.settings.arch == "x86_64":
                    rc = "windres --target=pe-x86-64"
                elif self.settings.arch == "x86":
                    rc = "windres --target=pe-i386"
                if self._is_clang_cl:
                    return os.environ.get("CC", "clang-cl"), os.environ.get("AR", "llvm-lib"), os.environ.get("LD", "lld-link"), rc
                if is_msvc(self):
                    return "cl -nologo", "lib", "link", rc
                    
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
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

            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure("gettext-tools")
        autotools.make()

    def package(self):
        dest_lib_dir = os.path.join(self.package_folder, "lib")
        dest_runtime_dir = os.path.join(self.package_folder, "bin")
        dest_include_dir = os.path.join(self.package_folder, "include")
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*gnuintl*.dll", self.build_folder, dest_runtime_dir, keep_path=False)
        copy(self, "*gnuintl*.lib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.a", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.so*", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*gnuintl*.dylib", self.build_folder, dest_lib_dir, keep_path=False)
        copy(self, "*libgnuintl.h", self.build_folder, dest_include_dir, keep_path=False)
        rename(self, os.path.join(dest_include_dir, "libgnuintl.h"), os.path.join(dest_include_dir, "libintl.h"))
        if (is_msvc(self) or self._is_clang_cl) and self.options.shared:
            rename(self, os.path.join(dest_lib_dir, "gnuintl.dll.lib"), os.path.join(dest_lib_dir, "gnuintl.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Intl")
        self.cpp_info.set_property("cmake_target_name", "Intl::Intl")
        self.cpp_info.libs = ["gnuintl"]
        if is_apple_os(self):
            self.cpp_info.frameworks.append("CoreFoundation")

        self.cpp_info.names["cmake_find_package"] = "Intl"
        self.cpp_info.names["cmake_find_package_multi"] = "Intl"
