import os
import shutil

from conan import ConanFile
from conan.tools import CppInfo
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path

required_conan_version = ">=2.0.5"


class CoinUtilsConan(ConanFile):
    name = "coin-utils"
    description = (
        "CoinUtils is an open-source collection of classes and helper "
        "functions that are generally useful to multiple COIN-OR projects."
    )
    topics = ("coin", "sparse", "matrix", "helper", "parsing", "representation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/CoinUtils"
    license = "EPL-2.0"

    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_glpk": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_glpk": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("openblas/0.3.28")
        if self.options.with_glpk:
            self.requires("glpk/4.48")  # v4.49+ are not supported due to dropped lpx_* functions

    def build_requirements(self):
        self.tool_requires("coin-buildtools/0.8.11")
        self.tool_requires("gnu-config/cci.20210814")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        deps = PkgConfigDeps(self)
        deps.generate()

        def _add_pkg_config_alias(src_name, dst_name):
            shutil.copy(os.path.join(self.generators_folder, f"{src_name}.pc"),
                        os.path.join(self.generators_folder, f"{dst_name}.pc"))

        _add_pkg_config_alias("openblas", "coinblas")
        _add_pkg_config_alias("openblas", "coinlapack")
        if self.options.with_glpk:
            _add_pkg_config_alias("glpk", "coinglpk")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            # the coin*.pc pkg-config files are only used when set to BUILD
            "--with-blas=BUILD",
            "--with-lapack=BUILD",
            "--with-glpk=BUILD" if self.options.with_glpk else "--without-glpk",
            # These are only used for sample datasets
            "--without-netlib",
            "--without-sample",
            "--disable-dependency-linking",
            "F77=unavailable",
        ])
        if self.settings.os in ["Linux", "FreeBSD"]:
            # enables compilation of thread aware CoinUtils
            # requires pthreads and rt
            tc.configure_args.append("--enable-coinutils-threads")
        # TODO: maybe add as options
        # tc.configure_args.append("--enable-coinutils-mempool-override-new")
        # tc.configure_args.append("--enable-coinutils-mempool-maxpooled=value")
        if is_msvc(self):
            tc.configure_args.append(f"--enable-msvc={self.settings.compiler.runtime}")
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

        if is_msvc(self):
            # Custom AutotoolsDeps for cl like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            cpp_info = CppInfo(self)
            for dependency in self.dependencies.values():
                cpp_info.merge(dependency.cpp_info.aggregated_components())
            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in cpp_info.includedirs] + [f"-D{d}" for d in cpp_info.defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in cpp_info.libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in cpp_info.libdirs] + cpp_info.sharedlinkflags + cpp_info.exelinkflags)
            env.append("CXXFLAGS", cpp_info.cxxflags)
            env.append("CFLAGS", cpp_info.cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        copy(self, "*", os.path.join(self.dependencies.build["coin-buildtools"].package_folder, "res"),
             os.path.join(self.source_folder, "BuildTools"))
        copy(self, "*", os.path.join(self.dependencies.build["coin-buildtools"].package_folder, "res"),
             os.path.join(self.source_folder, "CoinUtils", "BuildTools"))
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        # Manually specify OpenBLAS name mangling since F77 is not available to autodetect it.
        save(self, os.path.join(self.build_folder, "CoinUtils/src/config.h"),
             ("\n"
              "#define F77_FUNC(name,NAME) name ## _\n"
              "#define F77_FUNC_(name,NAME) name ## _\n"),
             append=True)
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(args=["-j1"])
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        if is_msvc(self):
            rename(self, os.path.join(self.package_folder, "lib", "libCoinUtils.a"),
                         os.path.join(self.package_folder, "lib", "CoinUtils.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "coinutils")
        self.cpp_info.libs = ["CoinUtils"]
        self.cpp_info.includedirs.append(os.path.join("include", "coin"))
        if not self.options.shared:
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.system_libs = ["m", "pthread", "rt"]
            if is_apple_os(self):
                self.cpp_info.frameworks.append("Accelerate")
