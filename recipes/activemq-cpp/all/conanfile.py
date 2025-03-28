from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, mkdir, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
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
    # In case having config_options() or configure() method, the logic should be moved to the specific methods.
    implements = ["auto_shared_fpic"]

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("apr/1.7.4")
        self.requires("openssl/[>=1.0.0]")

    def validate(self):
        # Always comment the reason including the upstream issue.
        # INFO: Upstream only support Unix systems. See <URL>
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")

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
        # autotools usually uses 'yes' and 'no' to enable/disable options
        def yes_no(v): return "yes" if v else "no"
        tc.autoreconf_args.extend(["-I", "config", "-I", "m4"])
        if self.options.shared:
            tc.configure_args.extend(["--enable-shared"])

        # Handle the fact that the library uses deprecated throws() declarations
        compiler_std = self.settings.get_safe('self.settings.compiler.cppstd')
        if compiler_std is None or compiler_std > 14:
            tc.extra_cxxflags.append('-std=c++14')

        tc.generate()
        # generate pkg-config files of dependencies (useless if upstream configure.ac doesn't rely on PKG_CHECK_MODULES macro)
        tc = PkgConfigDeps(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)

        script_folder = "activemq-cpp"

        if conan_version >= Version("2.0.2"):
            autotools.autoreconf(build_script_folder=script_folder)
        else:
            with chdir(self, os.path.join(self.source_folder, script_folder)):
                mkdir(self, "config")
                command = "autoreconf --force --install -I config -I m4"
                self.run(command)
        
        autotools.configure(build_script_folder=script_folder)
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
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
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
