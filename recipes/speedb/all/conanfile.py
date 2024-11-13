from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class SpeedbConan(ConanFile):
    name = "speedb"
    description = "A RocksDB compliant high performance scalable embedded key-value store"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/speedb-io/speedb"
    topics = ("rocksdb", "embedded", "key-value-store", "kvs", "storage-engine")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False],
        "with_lz4": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_core_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": True,
        "with_lz4": True,
        "with_zlib": True,
        "with_zstd": True,
        "with_core_tools": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TODO: support jemalloc, liburing
        if self.options.with_snappy:
            self.requires("snappy/1.1.10")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_core_tools:
            self.requires("gflags/2.2.2")
            self.requires("readline/8.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_JEMALLOC"] = False
        tc.variables["WITH_LIBURING"] = False
        tc.variables["WITH_SNAPPY"] = self.options.with_snappy
        tc.variables["WITH_LZ4"] = self.options.with_lz4
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        tc.variables["WITH_ZSTD"] = self.options.with_zstd
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_BENCHMARK_TOOLS"] = False
        tc.variables["WITH_CORE_TOOLS"] = self.options.with_core_tools
        tc.variables["WITH_GFLAGS"] = self.options.with_core_tools
        tc.variables["WITH_TOOLS"] = False
        tc.variables["ROCKSDB_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # to avoid wrong CPU detection, modify not to use "-march=native" in apple-clang
        if cross_building(self) and self.settings.compiler == "apple-clang":
            replace_in_file(self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                """elseif(NOT CMAKE_SYSTEM_PROCESSOR MATCHES "^(powerpc|ppc)64" AND NOT HAS_ARMV8_CRC)""",
                "elseif(FALSE)"
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["speedb"]
        self.cpp_info.set_property("pkg_config_name", "speedb")
        self.cpp_info.set_property("cmake_file_name", "Speedb")
        self.cpp_info.set_property("cmake_target_name", "Speedb::speedb")
