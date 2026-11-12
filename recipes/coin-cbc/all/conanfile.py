from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, rm, get, export_conandata_patches, apply_conandata_patches, rmdir, mkdir
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, Autotools
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path

import os

required_conan_version = ">=2.0"

class CoinCbcConan(ConanFile):
    name = "coin-cbc"
    package_type = "library"
    description = "COIN-OR Branch-and-Cut solver"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
    license = ("EPL-2.0",)
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
    def layout(self):
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("coin-utils/2.11.9", transitive_headers=True)
        self.requires("coin-osi/0.108.7", transitive_headers=True)
        self.requires("coin-clp/1.17.7", transitive_headers=True)
        self.requires("coin-cgl/0.60.3")
        if is_msvc(self) and self.options.parallel:
            self.requires("pthreads4w/3.0.0")    

    def build_requirements(self):
        self.tool_requires("gnu-config/[*]")
        self.tool_requires("pkgconf/[>=1.7.4 <3]")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type="str"):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
    
    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc does not support shared builds on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        if cross_building(self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc shared not supported yet when cross-building")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = AutotoolsToolchain(self)

        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-cbc-parallel={}".format(yes_no(self.options.parallel)),
            "--without-blas",
            "--without-lapack",
        ])
        env = tc.environment()
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            tc.configure_args.append(f"--enable-msvc={msvc_runtime_flag(self)}")

            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", f"{compile_wrapper} link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")

            if self.options.parallel:
                pthreads4w_info = self.dependencies["pthreads4w"].cpp_info.aggregated_components()
                pthreads4w_libdir = pthreads4w_info.libdirs[0]
                pthreads4w_incdir = pthreads4w_info.includedirs[0]
                pthreads4w_lib = os.path.join(pthreads4w_libdir, pthreads4w_info.libs[0]) + ".lib"
                tc.configure_args.append(f"--with-pthreadsw32-lib={unix_path(self, pthreads4w_lib)}")
                tc.configure_args.append(f"--with-pthreadsw32-incdir={unix_path(self, pthreads4w_incdir)}")
        if self.settings_build.os == "Windows":
            # the coin-cbc configure script adds values to PKG_CONFIG_PATH before invoking pkg-config,
            # the paths with leading double slash // interfere with msys2 path conversions and prevent it from working
            # as a workaround, add the path as regular windows PATH
            env.define("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=os.path.join(self.source_folder, "Cbc"))

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Installation script expects include/coin to already exist
        mkdir(self, os.path.join(self.package_folder, "include", "coin"))
        autotools = Autotools(self)
        autotools.install()

        fix_apple_shared_install_name(self)

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libcbc"].libs = ["CbcSolver", "Cbc"]
        self.cpp_info.components["libcbc"].set_property("pkg_config_name", "cbc")
        self.cpp_info.components["libcbc"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["libcbc"].requires = ["coin-clp::osi-clp", "coin-utils::coin-utils", "coin-osi::coin-osi", "coin-cgl::coin-cgl"]
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.parallel:
            self.cpp_info.components["libcbc"].system_libs.append("pthread")
        if is_msvc(self) and self.options.parallel:
            self.cpp_info.components["libcbc"].requires.append("pthreads4w::pthreads4w")

        self.cpp_info.components["osi-cbc"].libs = ["OsiCbc"]
        self.cpp_info.components["osi-cbc"].set_property("pkg_config_name", "osi-cbc")
        self.cpp_info.components["osi-cbc"].requires = ["libcbc"]

