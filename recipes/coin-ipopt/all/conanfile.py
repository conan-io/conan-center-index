import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path

required_conan_version = ">=1.57.0"


class CoinClpConan(ConanFile):
    name = "coin-ipopt"
    description = "COIN-OR Interior Point Optimizer IPOPT"
    topics = ("optimization", "interior-point", "nonlinear", "nonconvex")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Ipopt"
    license = "EPL-2.0"

    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "intsize": [32, 64],
        "precision": ["single", "double"],
        "with_lapack": [True, False],
        "with_mumps": [True, False],
        "build_sipopt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "intsize": 32,
        "precision": "double",
        "with_lapack": True,
        "with_mumps": False,  # TODO: enable after merging https://github.com/conan-io/conan-center-index/pull/22466
        "build_sipopt": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lapack:
            self.requires("openblas/0.3.25")
        if self.options.with_mumps:
            self.requires("coin-mumps/3.0.5")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared builds on Windows are not supported yet")

        if not self.options.with_mumps:
            raise ConanInvalidConfiguration("At least one solver is required (currently only MUMPS is supported)")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
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
            "--disable-f77",
            "--disable-java",
            f"--with-int={self.options.intsize}",
            f"--with-precision={self.options.precision}",
            f"--with-lapack={yes_no(self.options.with_lapack)}",
            f"--with-mumps={yes_no(self.options.with_mumps)}",
            f"--enable-sipopt={yes_no(self.options.build_sipopt)}",
            "--with-asl=no",
            "--with-hsl=no",
            "--with-spral=no",
            "--with-dot=no",
        ]
        if self.options.with_lapack:
            dep_info = self.dependencies["openblas"].cpp_info.aggregated_components()
            lib_flags = " ".join([f"-l{lib}" for lib in dep_info.libs + dep_info.system_libs])
            tc.configure_args.append(f"--with-lapack-lflags=-L{dep_info.libdir} {lib_flags}")

        if is_msvc(self) and check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", f"{compile_wrapper} link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
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
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["ipopt"].set_property("pkg_config_name", "ipopt")
        self.cpp_info.components["ipopt"].libs = ["ipopt"]
        self.cpp_info.components["ipopt"].includedirs.append(os.path.join("include", "coin-or"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ipopt"].system_libs.append("m")
        if self.options.with_lapack:
            self.cpp_info.components["ipopt"].requires.append("openblas::openblas")
        if self.options.with_mumps:
            self.cpp_info.components["ipopt"].requires.append("coin-mumps::coin-mumps")

        if self.options.build_sipopt:
            self.cpp_info.components["sipopt"].set_property("pkg_config_name", "sipopt")
            self.cpp_info.components["sipopt"].libs = ["sipopt"]
            self.cpp_info.components["sipopt"].includedirs.append(os.path.join("include", "coin-or"))
            self.cpp_info.components["sipopt"].requires = ["ipopt"]
