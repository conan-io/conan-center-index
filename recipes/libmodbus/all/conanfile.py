from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path, VCVars
import os


required_conan_version = ">=1.51.3"


class LibmodbusConan(ConanFile):
    name = "libmodbus"
    description = "libmodbus is a free software library to send/receive data according to the Modbus protocol"
    homepage = "https://libmodbus.org/"
    topics = ("libmodbus", "modbus", "protocol", "industry", "automation")
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

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
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
        # --fpic is automatically managed when 'fPIC' option is declared
        # --enable/disable-shared is automatically managed when 'shared' option is declared
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--without-documentation")
        tc.configure_args.append("--disable-tests")
        # TODO: how to port this?
        """
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12":
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                autotools.flags.append("-FS")
        """
        tc.generate()
        # generate dependencies for pkg-config
        tc = PkgConfigDeps(self)
        tc.generate()
        # generate dependencies for autotools
        tc = AutotoolsDeps(self)
        tc.generate()

        # inject tools_require env vars in build context
        ms = VirtualBuildEnv(self)
        ms.generate()

        if self.settings.compiler == "Visual Studio":
            ms = VCVars(self)
            ms.define("CC", "cl -nologo")
            ms.define("CXX", "cl -nologo")
            ms.define("LD", "link -nologo")
            ms.define("AR", "{} \"lib -nologo -verbose\"".format(unix_path(self.deps_user_info["automake"].ar_lib)))
            ms.define("RANLIB", ":")
            ms.define("STRING", ":")
            ms.define("NM", "dumpbin -symbols")
            ms.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.shared:
            for decl in ("__declspec(dllexport)", "__declspec(dllimport)"):
                replace_in_file(self, os.path.join(self.source_folder, "src", "modbus.h"), decl, "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
         # run autoreconf to generate configure file
        autotools.autoreconf()
        # ./configure + toolchain file
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()

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
            self.cpp_info.system_libs = ["wsock32"]
