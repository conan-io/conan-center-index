import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file, save
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
    topics = ("data-science", "storage-engine", "s3", "sparse-data", "scientific-computing", "s3-storage",
              "arrays", "data-analysis", "dataframes", "dense-data", "sparse-arrays")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpp_api": [True, False],
        "s3": [True, False],
        "azure": [True, False],
        "gcs": [True, False],
        "serialization": [True, False],
        "webp": [True, False],
        "tools": [True, False],
        "remove_deprecations": [True, False],
        "verbose": [True, False],
        "stats": [True, False],
        "experimental_features": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpp_api": True,
        "s3": False,
        "azure": False,
        "gcs": False,
        "serialization": False,
        "webp": True,
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
        "serialization": "Enable TileDB Cloud support by building with support for query serialization.",
        "webp": "Support WebP compression",
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
        # https://github.com/TileDB-Inc/TileDB/blob/2.21.0/doc/dev/BUILD.md#prerequisites
        return {
            "gcc": "10",
            "clang": "10",
            "apple-clang": "14",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.serialization:
            self.options["libcurl"].with_zstd = True
        if self.options.azure:
            self.options["azure-sdk-for-cpp"]["azure-storage-blobs"] = True
        if self.options.s3:
            self.options["aws-sdk-cpp"].s3 = True
            self.options["aws-sdk-cpp"]["identity-management"] = True
            self.options["aws-sdk-cpp"].sts = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TileDB has no transitive header deps
        self.requires("bzip2/1.0.8")
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("lz4/1.9.4")
        self.requires("spdlog/1.14.1")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/[^1.5]")
        if self.settings.os != "Windows":
            self.requires("openssl/[>=1.1 <4]")
        self.requires("libmagic/5.45")
        if self.options.azure:
            self.requires("azure-sdk-for-cpp/1.11.3")
        if self.options.gcs:
            self.requires("google-cloud-cpp/2.28.0")
        if self.options.serialization:
            self.requires("capnproto/1.0.2")
            self.requires("libcurl/[>=7.78 <9]")
        if self.options.s3:
            self.requires("aws-sdk-cpp/1.11.352")
        if self.options.tools:
            self.requires("clipp/1.2.3")
        if self.options.webp:
            self.requires("libwebp/1.4.0")

        # TODO: unvendor
        #  - bitshuffle
        #  - blosc
        #  - boost::interprocess
        #  - nlohmann_json
        #  - tcb-span

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.serialization and not self.dependencies["libcurl"].options.with_zstd:
            raise ConanInvalidConfiguration("TileDB serialization requires libcurl with with_zstd option enabled.")
        if self.options.s3:
            aws_opts = self.dependencies["aws-sdk-cpp"].options
            if not (aws_opts.get_safe("s3") and aws_opts.get_safe("identity-management") and aws_opts.get_safe("sts")):
                raise ConanInvalidConfiguration(
                    f"TileDB S3 support requires aws-sdk-cpp with 's3', 'identity-management' and 'sts' options enabled."
                )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        strip_root = Version(self.version) < "2.28.0"
        get(self, **self.conan_data["sources"][self.version], strip_root=strip_root)

    def generate(self):
        tc = CMakeToolchain(self)
        # https://github.com/TileDB-Inc/TileDB/blob/2.26.1/cmake/Options/BuildOptions.cmake
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["TILEDB_AZURE"] = self.options.azure
        tc.cache_variables["TILEDB_CPP_API"] = self.options.cpp_api
        tc.cache_variables["TILEDB_DISABLE_AUTO_VCPKG"] = True
        tc.cache_variables["TILEDB_EXPERIMENTAL_FEATURES"] = self.options.experimental_features
        tc.cache_variables["TILEDB_GCS"] = self.options.gcs
        tc.cache_variables["TILEDB_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        tc.cache_variables["TILEDB_REMOVE_DEPRECATIONS"] = self.options.remove_deprecations
        tc.cache_variables["TILEDB_S3"] = self.options.s3
        tc.cache_variables["TILEDB_SERIALIZATION"] = self.options.serialization
        tc.cache_variables["TILEDB_STATS"] = self.options.stats
        tc.cache_variables["TILEDB_TESTS"] = False
        tc.cache_variables["TILEDB_TOOLS"] = self.options.tools
        tc.cache_variables["TILEDB_VERBOSE"] = self.options.verbose
        tc.cache_variables["TILEDB_WEBP"] = self.options.webp
        tc.cache_variables["TILEDB_WERROR"] = False
        # Disable ExternalProject just in case
        tc.cache_variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        tc.cache_variables["libmagic_DICTIONARY"] = os.path.join(self.dependencies["libmagic"].package_folder, "res", "magic.mgc").replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        conan_to_cmake_name = {
            "aws-sdk-cpp": "AWSSDK",
            "azure-sdk-for-cpp": "azure-storage-blobs-cpp",
            "bzip2": "BZip2",
            "capnproto": "CapnProto",
            "clipp": "clipp",
            "google-cloud-cpp": "google_cloud_cpp_storage",
            "libcurl": "CURL",
            "libmagic": "unofficial-libmagic",
            "libwebp": "WebP",
            "libxml2": "LibXml2",
            "lz4": "lz4",
            "openssl": "OpenSSL",
            "spdlog": "spdlog",
            "zlib": "ZLIB",
            "zstd": "zstd",
        }
        for conan_name, cmake_name in conan_to_cmake_name.items():
            deps.set_property(conan_name, "cmake_file_name", cmake_name)

        renamed_targets = {
            "azure-sdk-for-cpp::azure-storage-blobs": "Azure::azure-storage-blobs",
            "bzip2": "BZip2::BZip2",
            "clipp": "clipp::clipp",
            "google-cloud-cpp::storage": "google-cloud-cpp::storage",
            "libmagic": "unofficial::libmagic::libmagic",
            "libwebp::webp": "WebP::webp",
            "libwebp::webpdecoder": "WebP::webpdecoder",
            "libwebp::webpdemux": "WebP::webpdemux",
            "libwebp::webpmux": "WebP::libwebpmux",
            "lz4": "LZ4::LZ4",
            "zlib": "ZLIB::ZLIB",
            "zstd": "Zstd::Zstd" if Version(self.version) < "2.28.0" else "zstd::libzstd",
        }
        for component, new_target_name in renamed_targets.items():
            deps.set_property(component, "cmake_target_name", new_target_name)

        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Disable examples
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(examples)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(experimental/experimental_examples)", "")
        # Don't actually run vcpkg
        save(self, os.path.join(self.source_folder, "cmake", "Options", "TileDBToolchain.cmake"), "")
        # No such target defined in CCI
        if self.options.serialization:
            capnproto_bindir = self.dependencies['capnproto'].cpp_info.bindir
            replace_in_file(self, os.path.join(self.source_folder, "tiledb", "CMakeLists.txt"),
                            "set(CAPNP_PLUGIN_DIR $<TARGET_FILE_DIR:CapnProto::capnp_tool>)",
                            f'set(CAPNP_PLUGIN_DIR "{capnproto_bindir}")')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # tools are not installed by CMake
        if self.options.tools:
            suffix = ".exe" if self.settings.os == "Windows" else ""
            copy(self, f"tiledb{suffix}",
                 src=os.path.join(self.build_folder, "tools"),
                 dst=os.path.join(self.package_folder, "bin"),
                 keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TileDB")
        suffix = "shared" if self.options.shared else "static"
        self.cpp_info.set_property("cmake_target_name", f"TileDB::tiledb_{suffix}")
        self.cpp_info.set_property("cmake_target_aliases", ["TileDB::tiledb"])
        self.cpp_info.set_property("pkg_config_name", "tiledb")

        self.cpp_info.libs = ["tiledb"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
        if stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
