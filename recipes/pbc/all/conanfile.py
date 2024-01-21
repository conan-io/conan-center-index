import os

from conan import ConanFile
from conan.tools.apple import XCRun, to_apple_arch
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class PbcConan(ConanFile):
    name = "pbc"
    description = ("The PBC (Pairing-Based Crypto) library is a C library providing "
                   "low-level routines for pairing-based cryptosystems.")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://crypto.stanford.edu/pbc/"
    topics = ("crypto", "cryptography", "security", "pairings", "cryptographic")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
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
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("automake/1.16.5")
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("LEX=flex")
        # No idea why this is necessary, but if you don't set CC this way, then
        # configure complains that it can't find gmp.
        if cross_building(self) and self.settings.compiler == "apple-clang":
            xcr = XCRun(self)
            target = to_apple_arch(self) + "-apple-darwin"
            min_ios = ""
            if self.settings.os == "iOS":
                min_ios = f"-miphoneos-version-min={self.settings.os.version}"
            tc.configure_args.append(f"CC={xcr.cc} -isysroot {xcr.sdk_path} -target {target} {min_ios}")
        tc.generate()

        if not is_msvc(self):
            deps = AutotoolsDeps(self)
            deps.generate()
        else:
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            gmp_info = self.dependencies["gmp"].cpp_info
            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in gmp_info.includedirs] + [f"-D{d}" for d in gmp_info.defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in (gmp_info.libs + gmp_info.system_libs)])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in gmp_info.libdirs] + gmp_info.sharedlinkflags + gmp_info.exelinkflags)
            env.append("CFLAGS", gmp_info.cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        apply_conandata_patches(self)
        configure = os.path.join(self.source_folder, "configure")
        # The check for bison/yacc is overly strict and fails for winflexbison
        replace_in_file(self, configure,
                        'if test "x$YACC" != "xbison -y"; then',
                        "if false; then")
        if is_msvc(self):
            # Skip -lm check
            replace_in_file(self, configure,
                            'if test "x$ac_cv_lib_m_pow" = xyes; then :',
                            "if true; then :")
            replace_in_file(self, configure, 'LIBS="-lm $LIBS"', "")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            if is_msvc(self):
                # Drop GCC/Clang flags
                replace_in_file(self, "Makefile", "CFLAGS = ", "CFLAGS = # ")
            autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["pbc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
