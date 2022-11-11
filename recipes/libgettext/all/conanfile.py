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
        return str(self.settings.compiler) in ["clang"] and str(self.settings.os) in ["Windows"] or \
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
        tc.generate()

        AutotoolsDeps(self).generate()

        if is_msvc(self) or self._is_clang_cl:
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        src_intl_dir = os.path.join(self.build_folder, "gettext-runtime", "intl")
        src_lib_dir = os.path.join(src_intl_dir, ".libs")
        dest_lib_dir = os.path.join(self.package_folder, "lib")
        dest_runtime_dir = os.path.join(self.package_folder, "bin")
        dest_include_dir = os.path.join(self.package_folder, "include")
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*gnuintl*.dll", src_lib_dir, dest_runtime_dir)
        copy(self, "*gnuintl*.lib", src_lib_dir, dest_lib_dir)
        copy(self, "*gnuintl*.a", src_lib_dir, dest_lib_dir)
        copy(self, "*gnuintl*.so*", src_lib_dir, dest_lib_dir)
        copy(self, "*gnuintl*.dylib", src_lib_dir, dest_lib_dir)
        copy(self, "*libgnuintl.h", src_intl_dir, dest_include_dir)
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
