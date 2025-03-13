import shutil

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, mkdir, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, msvc_runtime_flag
import os

required_conan_version = ">=2.1.0"


class CoinClpConan(ConanFile):
    name = "coin-clp"
    description = "COIN-OR Linear Programming Solver"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
    license = "EPL-2.0"
    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Symbols are exposed https://github.com/conan-io/conan-center-index/pull/16053#issuecomment-1512637106
        self.requires("coin-utils/2.11.11", transitive_headers=True, transitive_libs=True)
        self.requires("coin-osi/0.108.10", transitive_headers=True)
        self.requires("openblas/0.3.28")

        # TODO:
        # self.requires("metis/5.2.1")
        # self.requires("coin-mumps/3.0.5")
        # self.requires("suitesparse-amd/3.3.2")
        # self.requires("suitesparse-cholmod/5.2.1")
        # Not yet available on CCI: ASL, WSMP

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

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        def _add_pkg_config_alias(src_name, dst_name):
            shutil.copy(os.path.join(self.generators_folder, f"{src_name}.pc"),
                        os.path.join(self.generators_folder, f"{dst_name}.pc"))

        _add_pkg_config_alias("openblas", "coinblas")
        _add_pkg_config_alias("openblas", "coinlapack")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            # the coin*.pc pkg-config files are only used when set to BUILD
            "--with-blas=BUILD",
            "--with-lapack=BUILD",
            "--with-glpk=no", # GLPK is used as a substitute for AMD, but fails with undefined symbols
            # TODO
            "--without-asl",
            "--without-mumps",
            "--without-wsmp",
            "--disable-amd-libcheck",
            "--disable-cholmod-libcheck",
            # These are only used for sample datasets
            "--without-netlib",
            "--without-sample",
            "--disable-dependency-linking",
            "F77=unavailable",
        ])

        # TODO: add option
        # 1 - build Abc serial but no inherit code
        # 2 - build Abc serial and inherit code
        # 3 - build Abc cilk parallel but no inherit code
        # 4 - build Abc cilk parallel and inherit code
        # [AC_HELP_STRING([--enable-aboca],[enables build of Aboca solver (set to 1,2,3,4)])],

        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            tc.configure_args.append(f"--enable-msvc={msvc_runtime_flag(self)}")
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", f"{compile_wrapper} link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
        if self.settings_build.os == "Windows":
            # TODO: Something to fix in conan client or pkgconf recipe?
            # This is a weird workaround when build machine is Windows. Here we have to inject regular
            # Windows path to pc files folder instead of unix path flavor injected by AutotoolsToolchain...
            env.define("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate(env)

    def build(self):
        copy(self, "*", os.path.join(self.dependencies.build["coin-buildtools"].package_folder, "res"),
             os.path.join(self.source_folder, "BuildTools"))
        copy(self, "*", os.path.join(self.dependencies.build["coin-buildtools"].package_folder, "res"),
             os.path.join(self.source_folder, "Clp", "BuildTools"))
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Installation script expects include/coin to already exist
        mkdir(self, os.path.join(self.package_folder, "include", "coin"))
        autotools = Autotools(self)
        autotools.install(args=["-j1"])
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        if is_msvc(self):
            for l in ("Clp", "ClpSolver", "OsiClp"):
                rename(self, os.path.join(self.package_folder, "lib", f"lib{l}.a"),
                             os.path.join(self.package_folder, "lib", f"{l}.lib"))

    def package_info(self):
        self.cpp_info.components["clp"].set_property("pkg_config_name", "clp")
        self.cpp_info.components["clp"].libs = ["ClpSolver", "Clp"]
        self.cpp_info.components["clp"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["clp"].requires = ["coin-utils::coin-utils", "openblas::openblas"]

        self.cpp_info.components["osi-clp"].set_property("pkg_config_name", "osi-clp")
        self.cpp_info.components["osi-clp"].libs = ["OsiClp"]
        self.cpp_info.components["osi-clp"].requires = ["clp", "coin-osi::coin-osi"]
