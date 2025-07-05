from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

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

    def validate(self):
        # Always comment the reason including the upstream issue.
        # INFO: Upstream only support Unix systems. See <URL>
        if self.settings.os not in ["Linux", "FreeBSD", "MacOS", "Windows"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

        check_min_cppstd(self, 11)

        # Handle the fact that the library uses deprecated throws() declarations
        # check for the max CPP standard version and set it to 14 if it is newer
        compiler_std = self.settings.get_safe('self.settings.compiler.cppstd')
        if compiler_std is None or compiler_std > 14:
            tc = AutotoolsToolchain(self)
            tc.extra_cxxflags.append('-std=c++14')

    # if a tool other than the compiler or autotools is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("libtool/[>=1.5.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        # inject required env vars into the build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
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
        # generate pkg-config files of dependencies (useless if upstream configure.ac doesn't rely on PKG_CHECK_MODULES macro)
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

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # In shared lib/executable files, autotools set install_name (macOS) to lib dir absolute path instead of @rpath, it's not relocatable, so fix it
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.includedirs = ["include/activemq-cpp-3.9.5"]
        self.cpp_info.libs = ["activemq-cpp"]

        # if the package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "activemq-cpp")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD", "MacOS"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
