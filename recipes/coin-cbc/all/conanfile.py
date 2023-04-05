from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, msvc_runtime_flag, unix_path
import os

required_conan_version = ">=1.57.0"


class CoinCbcConan(ConanFile):
    name = "coin-cbc"
    description = "COIN-OR Branch-and-Cut solver"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
    license = "EPL-2.0"
    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "parallel": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "parallel": False,
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("coin-utils/2.11.6")
        self.requires("coin-osi/0.108.7")
        self.requires("coin-clp/1.17.7")
        self.requires("coin-cgl/0.60.6")
        if is_msvc(self) and self.options.parallel:
            self.requires("pthreads4w/3.0.0")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc does not support shared builds on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        if hasattr(self, "settings_build") and cross_building(self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc shared not supported yet when cross-building")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-cbc-parallel={yes_no(self.options.parallel)}",
            "--without-blas",
            "--without-lapack",
        ])
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            tc.configure_args.append(f"--enable-msvc={msvc_runtime_flag(self)}")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
                tc.extra_cxxflags.append("-FS")
            if self.options.parallel:
                pthreads4w_cpp_info = self.dependencies["pthreads4w"].cpp_info.aggregated_components()
                pthreads4w_lib = os.path.join(pthreads4w_cpp_info.libdirs[0], f"{pthreads4w_cpp_info.libs[0]}.lib")
                pthreads4w_includedir = pthreads4w_cpp_info.includedirs[0]
                tc.configure_args.extend([
                    f"--with-pthreadsw32-lib={unix_path(self, pthreads4w_lib)}",
                    f"--with-pthreadsw32-incdir={unix_path(self, pthreads4w_includedir)}",
                ])
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", f"{compile_wrapper} link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        if self._settings_build.os == "Windows":
            # TODO: Something to fix in conan client or pkgconf recipe?
            # This is a weird workaround when build machine is Windows. Here we have to inject regular
            # Windows path to pc files folder instead of unix path flavor injected by AutotoolsToolchain...
            env.define("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if not is_msvc(self):
            for gnu_config in [
                self.conf.get("user.gnu-config:config_guess", check_type=str),
                self.conf.get("user.gnu-config:config_sub", check_type=str),
            ]:
                if gnu_config:
                    copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        autotools = Autotools(self)
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
            for l in ("CbcSolver", "Cbc", "OsiCbc"):
                rename(self, os.path.join(self.package_folder, "lib", f"lib{l}.a"),
                             os.path.join(self.package_folder, "lib", f"{l}.lib"))

    def package_info(self):
        self.cpp_info.components["libcbc"].set_property("pkg_config_name", "cbc")
        self.cpp_info.components["libcbc"].libs = ["CbcSolver", "Cbc"]
        self.cpp_info.components["libcbc"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["libcbc"].requires = [
            "coin-clp::osi-clp", "coin-utils::coin-utils",
            "coin-osi::coin-osi", "coin-cgl::coin-cgl",
        ]
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.parallel:
            self.cpp_info.components["libcbc"].system_libs.append("pthread")
        if is_msvc(self) and self.options.parallel:
            self.cpp_info.components["libcbc"].requires.append("pthreads4w::pthreads4w")

        self.cpp_info.components["osi-cbc"].set_property("pkg_config_name", "osi-cbc")
        self.cpp_info.components["osi-cbc"].libs = ["OsiCbc"]
        self.cpp_info.components["osi-cbc"].requires = ["libcbc"]

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
