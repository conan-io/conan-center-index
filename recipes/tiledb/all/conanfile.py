import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file, rm, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class TileDBConan(ConanFile):
    name = "tiledb"
    description = ("TileDB is a powerful engine for storing and accessing dense and sparse multi-dimensional arrays, "
                   "which can help you model any complex data efficiently.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TileDB-Inc/TileDB"
    topics = ("data science", "storage engine", "s3", "sparse data", "scientific computing", "s3 storage",
              "arrays", "hdfs", "data analysis", "dataframes", "dense data", "sparse arrays")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpp_api": [True, False],
        "s3": [True, False],
        "azure": [True, False],
        "gcs": [True, False],
        "hdfs": [True, False],
        "serialization": [True, False],
        "webp": [True, False],
        "crc32": [True, False],
        "tools": [True, False],
        "remove_deprecations": [True, False],
        "verbose": [True, False],
        "stats": [True, False],
        "experimental_features": [True, False],
    }
    # Defaults are based on
    # https://github.com/TileDB-Inc/TileDB/blob/2.16.3/bootstrap#L89-L117
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpp_api": True,
        "s3": False,
        "azure": False,
        "gcs": False,
        "hdfs": False,
        "serialization": False,
        "webp": True,
        "crc32": False,
        "tools": False,
        "remove_deprecations": False,
        "verbose": False,
        "stats": True,
        "experimental_features": False,
    }
    options_description = {
        "cpp_api": "Enable building of the TileDB C++ API",
        "s3": "Support AWS S3 Storage",
        "azure": "Support Azure Blob Storage",
        "gcs": "Support Google Cloud Storage",
        "hdfs": "Support HDFS",
        "serialization": "Enable TileDB Cloud support by building with support for query serialization.",
        "webp": "Support WebP compression",
        "crc32": "Support CRC32",
        "tools": "Build tiledb command-line tool",
        "remove_deprecations": "Do not build deprecated APIs",
        "verbose": "Print TileDB errors with verbosity",
        "stats": "Enable internal TileDB statistics gathering",
        "experimental_features": "Build and include experimental features",
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "10",
            "apple-clang": "10",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.serialization:
            self.options["libcurl"].with_zstd = True
        if self.options.s3:
            self.options["aws-sdk-cpp"].s3 = True
            self.options["aws-sdk-cpp"]["identity-management"] = True
            self.options["aws-sdk-cpp"].sts = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TileDB has no transitive header deps
        self.requires("bzip2/1.0.8")
        self.requires("libxml2/2.11.5")
        self.requires("lz4/1.9.4")
        self.requires("spdlog/1.12.0")
        self.requires("xz_utils/5.4.4")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5")
        if self.settings.os != "Windows":
            self.requires("openssl/[>=1.1 <4]")
        self.requires("libmagic/5.45")
        if self.options.azure:
            # TODO: add azure-storage-blobs-cpp to CCI
            self.requires("azure-storage-blobs-cpp/12.6.1")
            if self.settings.os == "Windows":
                self.requires("wil/1.0.231028.1")
        if self.options.gcs:
            self.requires("google-cloud-cpp/2.12.0")
        if self.options.serialization:
            self.requires("libcurl/[>=7.78.0 <9]")
            # Exactly v0.8.0 is required
            self.requires("capnproto/0.8.0")
        if self.options.s3:
            self.requires("aws-sdk-cpp/1.9.234")
        if self.options.tools:
            self.requires("clipp/1.2.3")
        if self.options.webp:
            self.requires("libwebp/1.3.2")
        if self.options.crc32:
            self.requires("crc32c/1.1.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # https://github.com/TileDB-Inc/TileDB/blob/2.16.3/cmake/Options/BuildOptions.cmake
        tc.cache_variables["TILEDB_S3"] = self.options.s3
        tc.cache_variables["TILEDB_AZURE"] = self.options.azure
        tc.cache_variables["TILEDB_GCS"] = self.options.gcs
        tc.cache_variables["TILEDB_HDFS"] = self.options.hdfs
        tc.cache_variables["TILEDB_CPP_API"] = self.options.cpp_api
        tc.cache_variables["TILEDB_STATS"] = self.options.stats
        tc.cache_variables["TILEDB_STATIC"] = not self.options.shared
        tc.cache_variables["TILEDB_TOOLS"] = self.options.tools
        tc.cache_variables["TILEDB_SERIALIZATION"] = self.options.serialization
        tc.cache_variables["TILEDB_CRC32"] = self.options.crc32
        tc.cache_variables["TILEDB_WEBP"] = self.options.webp
        tc.cache_variables["TILEDB_EXPERIMENTAL_FEATURES"] = self.options.experimental_features
        tc.cache_variables["TILEDB_REMOVE_DEPRECATIONS"] = self.options.remove_deprecations
        tc.cache_variables["TILEDB_VERBOSE"] = self.options.verbose
        tc.cache_variables["TILEDB_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        tc.cache_variables["TILEDB_LOG_OUTPUT_ON_FAILURE"] = True
        tc.cache_variables["TILEDB_WERROR"] = False
        tc.cache_variables["TILEDB_TESTS"] = False
        tc.cache_variables["SANITIZER"] = False
        tc.cache_variables["TILEDB_SUPERBUILD"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        conan_to_cmake_name = {
            "aws-sdk-cpp": "AWSSDK",
            "azure-core-cpp": "AzureCore",
            "azure-storage-blobs-cpp": "AzureStorageBlobs",
            "azure-storage-common-cpp": "AzureStorageCommon",
            "bzip2": "Bzip2",
            "capnproto": "Capnp",
            "clipp": "Clipp",
            "crc32c": "crc32c",
            "google-cloud-cpp": "GCSSDK",
            "libcurl": "Curl",
            "libmagic": "Magic",
            "libwebp": "Webp",
            "lz4": "LZ4",
            "magic": "Magic",
            "openssl": "OpenSSL",
            "spdlog": "Spdlog",
            "wil": "WIL",
            "zlib": "Zlib",
            "zstd": "Zstd",
        }
        for conan_name, cmake_name in conan_to_cmake_name.items():
            deps.set_property(conan_name, "cmake_find_mode", "config")
            deps.set_property(conan_name, "cmake_file_name", cmake_name)

        renamed_targets = {
            "bzip2":                     "Bzip2::Bzip2",
            "clipp":                     "Clipp::Clipp",
            "google-cloud-cpp::storage": "storage_client",
            "libmagic":                  "libmagic",
            "libwebp::webp":             "WebP::webp",
            "libwebp::webpdecoder":      "WebP::webpdecoder",
            "libwebp::webpdemux":        "WebP::webpdemux",
            "libwebp::webpmux":          "WebP::libwebpmux",
            "lz4":                       "LZ4::LZ4",
            "zlib":                      "ZLIB::ZLIB",
            "zstd":                      "Zstd::Zstd",
        }
        for component, new_target_name in renamed_targets.items():
            deps.set_property(component, "cmake_target_name", new_target_name)

        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable examples
        # Re-add external includes, which otherwise used to get added via cmake/Modules/Find*_EP.cmake modules
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(examples)",
                        "include_directories(external/include)")
        # Replace ExternalProject packages with Conan versions,
        # e.g. find_package(Bzip2_EP REQUIRED) with find_package(Bzip2 REQUIRED CONFIG)
        for path in self.source_path.rglob("CMakeLists.txt"):
            replace_in_file(self, path, "_EP REQUIRED", " REQUIRED CONFIG", strict=False)
        # Remove all _EP modules, just in case
        rm(self, "*_EP.cmake", os.path.join(self.source_path, "cmake", "Modules"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        # Plain cmake.install() does not work. Needs to be run from the tiledb subdirectory.
        self.run(f"cmake --install {self.build_path / 'tiledb'}")
        # tools are not installed by CMake
        if self.options.tools:
            suffix = ".exe" if self.settings.os == "Windows" else ""
            copy(self, f"tiledb{suffix}",
                 dst=os.path.join(self.package_folder, "bin"),
                 src=os.path.join(self.build_folder, "tiledb", "tools"),
                 keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # TileDB always builds shared libraries
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll*", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TileDB")
        suffix = "shared" if self.options.shared else "static"
        self.cpp_info.set_property("cmake_target_name", f"TileDB::tiledb_{suffix}")
        self.cpp_info.set_property("cmake_target_aliases", ["TileDB::tiledb"])
        self.cpp_info.set_property("pkg_config_name", "tiledb")

        self.cpp_info.libs = ["tiledb"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
