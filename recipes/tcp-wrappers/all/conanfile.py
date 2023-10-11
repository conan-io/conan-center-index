import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class TcpWrappersConan(ConanFile):
    name = "tcp-wrappers"
    description = "A security tool which acts as a wrapper for TCP daemons"
    license = "BSD"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ftp.porcupine.org/pub/security/"
    topics = ("tcp", "ip", "daemon", "wrapper")

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio is not supported")
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross-building is not current supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _shext(self):
        if is_apple_os(self):
            return ".dylib"
        return ".so"

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args.append("REAL_DAEMON_DIR=/bin")
        tc.make_args.append(f"SHEXT={self._shext}")
        if self.options.shared:
            tc.make_args.append("shared=1")
        if self.options.get_safe("fPIC") or self.options.shared:
            tc.make_args.append("ENV_CFLAGS=-fPIC")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="linux")

    def package(self):
        copy(self, "DISCLAIMER",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        for exe in ("safe_finger", "tcpd", "tcpdchk", "tcpdmatch", "try-from"):
            copy(self, exe,
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "bin"),
                 keep_path=False)
        copy(self, "tcpd.h",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "include"),
             keep_path=False)
        if self.options.shared:
            copy(self, f"libwrap{self._shext}",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "lib"),
                 keep_path=False)
        else:
            copy(self, "libwrap.a",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "lib"),
                 keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["wrap"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
