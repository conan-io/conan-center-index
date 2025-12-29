import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_max_cppstd, check_min_cppstd, cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=2.1"

class PackageConan(ConanFile):
    name = "activemq-cpp"
    description = "JMS-like API for C++ for interfacing with Message Brokers such as Apache ActiveMQ"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/activemq-cpp"
    topics = ("ruby", "python", "c", "java", "php", "csharp", "cplusplus", "perl", "activemq", "network-server", "network-client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
        self.requires("apr/[>=1.3]")
        self.requires("apr-util/[>=1.3]")
        self.requires("libuuid/[>=1.0.3]")
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 11)
        check_max_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("libtool/[>=1.5.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        tc = AutotoolsToolchain(self)

        tc.autoreconf_args.extend(["-I", "config", "-I", "m4"])
        if self.options.shared:
            tc.configure_args.extend(["--enable-shared"])

        apr_package_folder = self.dependencies.direct_host["apr"].package_folder
        tc.configure_args.extend([
                f"--with-apr={apr_package_folder}"
            ])

        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)

        script_folder = "activemq-cpp"

        autotools.autoreconf(build_script_folder=script_folder)
        autotools.configure(build_script_folder=script_folder)
        autotools.make()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.includedirs = ["include/activemq-cpp-3.9.5"]
        self.cpp_info.libs = ["activemq-cpp"]

        self.cpp_info.set_property("pkg_config_name", "activemq-cpp")

        if self.settings.os in ["Linux", "FreeBSD", "Macos"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
