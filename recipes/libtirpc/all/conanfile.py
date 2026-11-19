from conan import ConanFile
from conan.tools.build import check_min_cstd
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.4"

class LibtirpcConan(ConanFile):
    name = "libtirpc"
    description = "Libtirpc is a port of Sun's Transport-Independent RPC library to Linux. It's being developed by the Bull GNU/Linux NFSv4 project."

    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libtirpc/"
    topics = ("libtirpc", "tirpc", "sun-rpc", "onc-rpc", "nfs", "rpc", "rpcgen")
    languages = "C"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gssapi": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gssapi": True
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.options.with_gssapi:
            # INFO: krb5-config tool is required to obtain the correct CFLAGS and LDFLAGS for krb5 dependency
            self.tool_requires("krb5/<host_version>")

    def requirements(self):
        if self.options.with_gssapi:
            self.requires("krb5/1.21.2")

    def validate(self):
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 99)
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} is only supported on Linux and FreeBSD")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-gssapi={}".format("yes" if self.options.with_gssapi else "no"))
        tc.generate()
        # INFO: In order to find AC_CHECK_HEADER(gssapi/gssapi.h) from krb5
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.libs = ["tirpc"]
        self.cpp_info.includedirs.append(os.path.join("include", "tirpc"))
        self.cpp_info.set_property("pkg_config_name", "libtirpc")
        self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
