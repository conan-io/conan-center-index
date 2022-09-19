from conan import ConanFile
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os


required_conan_version = ">=1.51.3"


class LibmodbusConan(ConanFile):
    name = "libmodbus"
    description = "libmodbus is a free software library to send/receive data according to the Modbus protocol"
    homepage = "https://libmodbus.org/"
    topics = ("modbus", "protocol", "industry", "automation")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC # once removed by config_options, need try..except for a second del
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx # for plain C projects only
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd # for plain C projects only
        except Exception:
            pass
        if self.settings.os == "Windows":
            self.win_bash = True

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("automake/1.16.3")
        # see https://github.com/conan-io/conan/issues/11969
        bash_path = os.getenv("CONAN_BASH_PATH") or self.conf.get("tools.microsoft.bash:path")
        if self.settings.os == "Windows" and not bash_path:
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self.source_folder, strip_root=True)

    def validate(self):
        # validate the minimum cpp standard supported
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--without-documentation")
        tc.configure_args.append("--disable-tests")

        # the following MSVC specific part has been ported from conan v1 following https://github.com/conan-io/conan-center-index/pull/12916
        if is_msvc(self) and Version(self.settings.compiler.version) >= "12":
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
    
        env = tc.environment()

        if is_msvc(self):
            ar_lib = unix_path(self, self.deps_user_info['automake'].ar_lib)
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_lib} lib")
            env.define("RANLIB", ":")
            env.define("STRING", ":")
            env.define("NM", "dumpbin -symbols")

        tc.generate(env)

        # generate dependencies for pkg-config
        tc = PkgConfigDeps(self)
        tc.generate()

        # generate dependencies for autotools
        tc = AutotoolsDeps(self)
        tc.generate()

        # inject tools_require env vars in build context
        ms = VirtualBuildEnv(self)
        ms.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.shared:
            for decl in ("__declspec(dllexport)", "__declspec(dllimport)"):
                replace_in_file(self, os.path.join(self.source_folder, "src", "modbus.h"), decl, "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        # see https://github.com/conan-io/conan/issues/12006
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        if is_apple_os(self):
            fix_apple_shared_install_name(self)

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            rename(self,
                    os.path.join(self.package_folder, "lib", "modbus.dll.lib"),
                    os.path.join(self.package_folder, "lib", "modbus.lib"))

    def package_info(self):
        self.cpp_info.libs = ["modbus"]

        # should this be kept for v1?
        # self.cpp_info.names["pkg_config"] = "libmodbus"
        self.cpp_info.set_property("pkg_config_name", "libmodbus")

        # self.cpp_info.includedirs.append(os.path.join("include", "modbus"))
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs = ["ws2_32"]
