from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.52.0"


class LevelDBCppConan(ConanFile):
    name = "leveldb"
    description = (
        "LevelDB is a fast key-value storage library written at Google that "
        "provides an ordered mapping from string keys to string values."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/leveldb"
    topics = ("leveldb", "google", "db")
    license = ("BSD-3-Clause",)

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False],
        "with_crc32c": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": True,
        "with_crc32c": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # FIXME: tcmalloc is also conditionally included in leveldb, but
        # there is no "official" conan package yet; when that is available, we
        # can add similar with options for those
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if self.options.with_crc32c:
            self.requires("crc32c/1.1.2")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LEVELDB_BUILD_TESTS"] = False
        tc.variables["LEVELDB_BUILD_BENCHMARKS"] = False
        tc.variables["HAVE_SNAPPY"] = self.options.with_snappy
        tc.variables["HAVE_CRC32C"] = self.options.with_crc32c
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "leveldb")
        self.cpp_info.set_property("cmake_target_name", "leveldb::leveldb")
        self.cpp_info.libs = ["leveldb"]
        if self.options.shared:
            self.cpp_info.defines.append("LEVELDB_SHARED_LIBRARY")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
