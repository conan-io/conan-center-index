from os.path import join
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, apply_conandata_patches
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.build import check_min_cppstd
import functools

required_conan_version = ">=1.50.0"

class NuRaftConan(ConanFile):
    name = "nuraft"
    homepage = "https://github.corp.ebay.com/sds/NuRaft"
    description = """Cornerstone based RAFT library."""
    topics = ("raft")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "compiler", "arch", "build_type"

    options = {
        "asio": ["boost", "standalone"],
        "shared": ['True', 'False'],
        "fPIC": ['True', 'False'],
    }
    default_options = {
        "asio": "boost",
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(p["patch_file"])

    def requirements(self):
        if self.options.asio == "boost":
            self.requires("boost/1.79.0")
        else:
            self.requires("asio/1.22.1")
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.os in ["Windows"]:
            raise ConanInvalidConfiguration("{} Builds are unsupported".format(self.info.settings.os))
        if self.info.settings.os in ["Macos"] and self.options.shared:
            raise ConanInvalidConfiguration("Building Shared Object for {} unsupported".format(self.info.settings.os))
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", self.source_folder, join(self.package_folder, "licenses/"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nuraft"]
        self.cpp_info.system_libs = ["m"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
