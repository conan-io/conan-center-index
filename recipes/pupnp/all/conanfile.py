import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class PupnpConan(ConanFile):
    name = "pupnp"
    description = (
        "The portable Universal Plug and Play (UPnP) SDK "
        "provides support for building UPnP-compliant control points, "
        "devices, and bridges on several operating systems."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pupnp/pupnp"
    topics = ("upnp", "networking")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ipv6": [True, False],
        "reuseaddr": [True, False],
        "webserver": [True, False],
        "client": [True, False],
        "device": [True, False],
        "largefile": [True, False],
        "tools": [True, False],
        "blocking-tcp": [True, False],
        "debug": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ipv6": True,
        "reuseaddr": True,
        "webserver": True,
        "client": True,
        "device": True,
        "largefile": True,
        "tools": True,
        "blocking-tcp": False,
        "debug": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            # Note, pupnp has build instructions for Visual Studio but they
            # include VC 6 and require pthreads-w32 library.
            # Someone who needs it and has possibility to build it could step in.
            raise ConanInvalidConfiguration("Visual Studio not supported yet in this recipe")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        features = {}
        features["samples"] = False
        features["blocking_tcp_connections"] = self.options["blocking-tcp"]
        for opt in ("ipv6", "reuseaddr", "webserver", "client", "device", "largefile", "tools", "debug"):
            features[opt] = self.options.get_safe(opt)
        for feature, enabled in features.items():
            what = "enable" if enabled else "disable"
            tc.configure_args.append(f"--{what}-{feature}")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libupnp")
        self.cpp_info.libs = ["upnp", "ixml"]
        self.cpp_info.includedirs.append(os.path.join("include", "upnp"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
            self.cpp_info.cflags.extend(["-pthread"])
            self.cpp_info.cxxflags.extend(["-pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["iphlpapi", "ws2_32"])
