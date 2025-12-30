import os
import shutil

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path
from conan.tools.scm import Version

required_conan_version = ">=2.1.0"

class CoinCbcConan(ConanFile):
    name = "coin-cbc"
    description = "COIN-OR Branch-and-Cut solver"
    topics = ("cbc", "branch-and-cut", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Cbc"
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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Roll version as part of modernizing to avoid a graph conflict
        self.requires("coin-utils/2.11.9")
        self.requires("coin-osi/0.108.7")
        self.requires("coin-clp/1.17.7", transitive_headers=True, transitive_libs=True)
        self.requires("coin-cgl/0.60.3", transitive_headers=True, transitive_libs=True)
        if is_msvc(self) and self.options.parallel:
            self.requires("pthreads4w/3.0.0")

    def build_requirements(self):
        # TODO: do we need coin-buildtools/0.8.11 here?
        self.tool_requires("gnu-config/cci.20201022")
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
        tc = PkgConfigDeps(self)
        tc.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--without-blas",
            "--without-lapack",
            ])

        if is_msvc(self):
            self.extra_cxxflags.append("-EHsc")
            tc.configure_args.append(f"--enable-msvc={msvc_runtime_flag(self)}")
            if self.options.parallel:
                pthreads4w_info = self.dependencies["pthreads4w"].cpp_info
                pthreads_path = os.path.join(pthreads4w_info.libdir, pthreads4w_info.libs[0] + ".lib")
                tc.configure_args.append("--with-pthreadsw32-lib={}".format(unix_path(self,pthreads_path)))
                tc.configure_args.append("--with-pthreadsw32-incdir={}".format(unix_path(self, pthreads4w_info.includedir)))
        tc.generate()

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
            env.vars(self).save_script("conanbuild_msvc")
        if self.settings_build.os == "Windows":
            env.define("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate(env)

    def build(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            config_folder = os.path.join(self.source_folder, "config")
            copy(self, os.path.basename(gnu_config),
                 src=os.path.dirname(gnu_config),
                 dst=config_folder)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # Installation script expects include/coin to already exist
        mkdir(self, os.path.join(self.package_folder, "include", "coin"))
        autotools = Autotools(self)
        autotools.install()

        for l in ("CbcSolver", "Cbc", "OsiCbc"):
            os.unlink(f"{self.package_folder}/lib/lib{l}.la")
            if is_msvc(self):
                rename(self,
                       f"{self.package_folder}/lib/lib{l}.a",
                       f"{self.package_folder}/lib/{l}.lib")

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libcbc"].set_property("pkg_config_name", "cbc")
        self.cpp_info.components["libcbc"].libs = ["CbcSolver", "Cbc"]
        self.cpp_info.components["libcbc"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["libcbc"].requires = ["coin-clp::osi-clp", "coin-utils::coin-utils", "coin-osi::coin-osi", "coin-cgl::coin-cgl"]
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.parallel:
            self.cpp_info.components["libcbc"].system_libs.append("pthread")
        if self.settings.os in ["Windows"] and self.options.parallel:
            self.cpp_info.components["libcbc"].requires.append("pthreads4w::pthreads4w")

        self.cpp_info.components["osi-cbc"].set_property("pkg_config_name", "osi-cbc")
        self.cpp_info.components["osi-cbc"].libs = ["OsiCbc"]
        self.cpp_info.components["osi-cbc"].requires = ["libcbc"]
