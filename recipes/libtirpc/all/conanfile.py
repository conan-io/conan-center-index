from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building, check_min_cstd
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=2.0.9"

class LibtirpcConan(ConanFile):
    name = "libtirpc"
    description = "Libtirpc is a port of Sun's Transport-Independent RPC library to Linux. It's being developed by the Bull GNU/Linux NFSv4 project."

    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libtirpc/"
    topics = ("libtirpc", "tirpc", "sun-rpc", "onc-rpc", "nfs", "rpc", "rpcgen")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ipv6": [True, False],
        "with_gssapi": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ipv6": False,
        "with_gssapi": False
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_gssapi:
            self.requires(f"krb5/1.21.2")

    def validate(self):
        if "cstd" in self.settings.compiler:
            check_min_cstd(self, 99)


    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.9.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        tc = AutotoolsToolchain(self)

        def enable_disable(v):
            return "enable" if v else "disable"

        tc.configure_args.extend([
            f"--enable-tools=no",
            "--enable-manpages=no",
            f"--{enable_disable(self.options.with_ipv6)}-ipv6",
            f"--{enable_disable(self.options.with_gssapi)}-gssapi"
        ])
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

        if is_msvc(self):
            env = Environment()
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
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        copy(self, "*", os.path.join(self.package_folder, "include", "tirpc"), os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "tirpc"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libtirpc"
        self.cpp_info.names["cmake_find_package_multi"] = "libtirpc"
        self.cpp_info.libs = ["tirpc"]

        self.cpp_info.set_property("pkg_config_name", "libtirpc")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
