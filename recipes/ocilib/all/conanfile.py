from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"

class OCILIBConan(ConanFile):
    name = "ocilib"
    description = "An open source and cross platform Oracle Driver that delivers efficient access to Oracle databases."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vrogier/ocilib"
    topics = ("database", "db", "sql", "oracle")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_oracle_charset": ["ansi", "wide"],
        "with_oracle_import": ["runtime", "linkage"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_oracle_charset": "ansi",
        "with_oracle_import": "runtime",
    }

    @property
    def _min_cppstd(self):
        return 11

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} recipe only supports Linux for now. Pull requests to add new configurtations are welcomed.")
        # TODO: Check support for other platforms

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--with-oracle-charset={self.options.with_oracle_charset}",
            f"--with-oracle-import={self.options.with_oracle_import}",
        ])
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "*.lib", self.source_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", self.source_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["ocilib"]
        self.cpp_info.set_property("pkg_config_name", "ocilib")
        self.cpp_info.system_libs.append("dl")
