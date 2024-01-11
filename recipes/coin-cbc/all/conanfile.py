import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, mkdir, rename, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CoinCbcConan(ConanFile):
    name = "coin-cbc"
    description = "COIN-OR Branch-and-Cut solver"
    license = ("EPL-2.0",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
    topics = ("clp", "simplex", "solver", "linear", "programming")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "parallel": [True, False]}
    default_options = {"shared": False, "fPIC": True, "parallel": False}

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

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc does not support shared builds on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        if hasattr(self, "settings_build") and cross_building(self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc shared not supported yet when cross-building")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        self.tool_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--enable-cbc-parallel={}".format(yes_no(self.options.parallel)),
            "--without-blas",
            "--without-lapack",
        ]
        if is_msvc(self):
            tc.cxxflags.append("-EHsc")
            tc.configure_args.append(f"--enable-msvc={msvc_runtime_flag(self)}")
            if Version(self.settings.compiler.version) >= 12:
                tc.cxxflags.append("-FS")
            if self.options.parallel:
                pthreads_path = os.path.join(
                    self.dependencies["pthreads4w"].cpp_info.libdirs[0],
                    self.dependencies["pthreads4w"].cpp_info.libs[0] + ".lib"
                )
                tc.configure_args.append("--with-pthreadsw32-lib={}".format(unix_path(self, pthreads_path)))
                tc.configure_args.append("--with-pthreadsw32-incdir={}".format(
                    unix_path(self, self.dependencies["pthreads4w"].cpp_info.includedirs[0]))
                )
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        apply_conandata_patches(self)
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                config_folder = os.path.join(self.source_folder, "config")
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=config_folder)

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Installation script expects include/coin to already exist
        mkdir(self, os.path.join(self.package_folder, "include", "coin"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()

        for l in ("CbcSolver", "Cbc", "OsiCbc"):
            os.unlink(f"{self.package_folder}/lib/lib{l}.la")
            if is_msvc(self):
                rename(self, f"{self.package_folder}/lib/lib{l}.a", f"{self.package_folder}/lib/{l}.lib")

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libcbc"].libs = ["CbcSolver", "Cbc"]
        self.cpp_info.components["libcbc"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["libcbc"].requires = [
            "coin-clp::osi-clp", "coin-utils::coin-utils", "coin-osi::coin-osi", "coin-cgl::coin-cgl"
        ]
        self.cpp_info.components["libcbc"].set_property("pkg_config_name", "cbc")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.parallel:
            self.cpp_info.components["libcbc"].system_libs.append("pthread")
        if self.settings.os in ["Windows"] and self.options.parallel:
            self.cpp_info.components["libcbc"].requires.append("pthreads4w::pthreads4w")

        self.cpp_info.components["osi-cbc"].libs = ["OsiCbc"]
        self.cpp_info.components["osi-cbc"].requires = ["libcbc"]
        self.cpp_info.components["osi-cbc"].set_property("pkg_config_name", "osi-cbc")

        # TODO: remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
