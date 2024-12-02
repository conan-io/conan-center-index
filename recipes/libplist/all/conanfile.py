from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=2.1"

class PackageConan(ConanFile):
    name = "libplist"
    description = "A small portable C library to handle Apple Property List files in binary, XML, JSON, or OpenStep format."
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libimobiledevice/libplist"
    topics = ("plist", "apple", "property list", "binary", "xml", "json", "openstep")

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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # It generates C++ bindings, but it is a C library
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("libplist does not support MSVC - use MinGW instead")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        tc = AutotoolsToolchain(self)

        tc.configure_args.extend([
            # No need for python bindings
            "--without-cython",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        #autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LESSER", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        #rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["plist-2.0"]
        self.cpp_info.set_property("pkg_config_name", "plist-2.0")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])

        if not self.options.shared:
            self.cpp_info.defines.append("LIBPLIST_STATIC")
