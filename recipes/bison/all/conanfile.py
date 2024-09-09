from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.54.0"


class BisonConan(ConanFile):
    name = "bison"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/bison/"
    description = "Bison is a general-purpose parser generator"
    topics = ("bison", "parser")
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("m4/1.4.19")

    def validate(self):
        if is_msvc(self) and self.version == "3.8.2":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not yet ready for Visual Studio, use previous version "
                "or open a pull request on https://github.com/conan-io/conan-center-index/pulls"
            )

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
        if self.settings.os != "Windows":
            self.tool_requires("flex/2.6.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-relocatable",
            "--disable-nls",
            "--datarootdir=${prefix}/res",
        ])
        if self.settings.compiler == "apple-clang":
            tc.configure_args.append("gl_cv_compiler_check_decl_option=")
        if is_msvc(self):
            # Avoid a `Assertion Failed Dialog Box` during configure with build_type=Debug
            # Visual Studio does not support the %n format flag:
            # https://docs.microsoft.com/en-us/cpp/c-runtime-library/format-specification-syntax-printf-and-wprintf-functions
            # Because the %n format is inherently insecure, it is disabled by default. If %n is encountered in a format string,
            # the invalid parameter handler is invoked, as described in Parameter Validation. To enable %n support, see _set_printf_count_output.
            tc.configure_args.extend([
                "gl_cv_func_printf_directive_n=no",
                "gl_cv_func_snprintf_directive_n=no",
                "gl_cv_func_snprintf_directive_n=no",
            ])
            tc.extra_cflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)

        makefile = os.path.join(self.source_folder, "Makefile.in")
        yacc = os.path.join(self.source_folder, "src", "yacc.in")

        if self.settings.os == "Windows":
            # replace embedded unix paths by windows paths
            replace_in_file(self, makefile,
                                  "echo '#define BINDIR \"$(bindir)\"';",
                                  "echo '#define BINDIR \"$(shell cygpath -m \"$(bindir)\")\"';")
            replace_in_file(self, makefile,
                                  "echo '#define PKGDATADIR \"$(pkgdatadir)\"';",
                                  "echo '#define PKGDATADIR \"$(shell cygpath -m \"$(pkgdatadir)\")\"';")
            replace_in_file(self, makefile,
                                  "echo '#define DATADIR \"$(datadir)\"';",
                                  "echo '#define DATADIR \"$(shell cygpath -m \"$(datadir)\")\"';")
            replace_in_file(self, makefile,
                                  "echo '#define DATAROOTDIR \"$(datarootdir)\"';",
                                  "echo '#define DATAROOTDIR \"$(shell cygpath -m \"$(datarootdir)\")\"';")

        replace_in_file(self, makefile,
                              "dist_man_MANS = $(top_srcdir)/doc/bison.1",
                              "dist_man_MANS =")
        replace_in_file(self, yacc, "@prefix@", "$CONAN_BISON_ROOT")
        replace_in_file(self, yacc, "@bindir@", "$CONAN_BISON_ROOT/bin")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.install()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        if is_msvc(self):
            rename(self, os.path.join(self.package_folder, "lib", "liby.a"),
                         os.path.join(self.package_folder, "lib", "y.lib"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libs = ["y"]
        self.cpp_info.resdirs = ["res"]

        bison_root = self.package_folder.replace("\\", "/")
        self.buildenv_info.define_path("CONAN_BISON_ROOT", bison_root)

        pkgdir = os.path.join(self.package_folder, "res", "bison")
        self.buildenv_info.define_path("BISON_PKGDATADIR", pkgdir)

        # yacc is a shell script, so requires a shell (such as bash)
        yacc = os.path.join(self.package_folder, "bin", "yacc").replace("\\", "/")
        self.conf_info.define("user.bison:yacc", yacc)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CONAN_BISON_ROOT = self.package_folder.replace("\\", "/")
        self.env_info.BISON_PKGDATADIR = pkgdir
        self.user_info.YACC = yacc
