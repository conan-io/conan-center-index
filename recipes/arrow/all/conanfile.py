from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

import os
import glob

required_conan_version = ">=1.53.0"

class ArrowConan(ConanFile):
    name = "arrow"
    description = "Apache Arrow is a cross-language development platform for in-memory data"
    license = ("Apache-2.0",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://arrow.apache.org/"
    topics = ("memory", "gandiva", "parquet", "skyhook", "acero", "hdfs", "csv", "cuda", "gcs", "json", "hive", "s3", "grpc")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "gandiva":  [True, False],
        "parquet": ["auto", True, False],
        "substrait": [True, False],
        "skyhook": [True, False],
        "acero": [True, False],
        "cli": [True, False],
        "compute": ["auto", True, False],
        "dataset_modules":  ["auto", True, False],
        "deprecated": [True, False],
        "encryption": [True, False],
        "filesystem_layer":  [True, False],
        "hdfs_bridgs": [True, False],
        "plasma": [True, False, "deprecated"],
        "simd_level": [None, "default", "sse4_2", "avx2", "avx512", "neon", ],
        "runtime_simd_level": [None, "sse4_2", "avx2", "avx512", "max"],
        "with_backtrace": [True, False],
        "with_boost": ["auto", True, False],
        "with_csv": [True, False],
        "with_cuda": [True, False],
        "with_flight_rpc":  ["auto", True, False],
        "with_flight_sql":  [True, False],
        "with_gcs": [True, False],
        "with_gflags": ["auto", True, False],
        "with_glog": ["auto", True, False],
        "with_grpc": ["auto", True, False],
        "with_jemalloc": ["auto", True, False],
        "with_mimalloc": [True, False],
        "with_json": [True, False],
        "with_thrift": ["auto", True, False],
        "with_llvm": ["auto", True, False],
        "with_openssl": ["auto", True, False],
        "with_opentelemetry": [True, False],
        "with_orc": [True, False],
        "with_protobuf": ["auto", True, False],
        "with_re2": ["auto", True, False],
        "with_s3": [True, False],
        "with_utf8proc": ["auto", True, False],
        "with_brotli": [True, False],
        "with_bz2": [True, False],
        "with_lz4": [True, False],
        "with_snappy": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "gandiva": False,
        "parquet": "auto",
        "skyhook": False,
        "substrait": False,
        "acero": False,
        "cli": False,
        "compute": "auto",
        "dataset_modules": "auto",
        "deprecated": True,
        "encryption": False,
        "filesystem_layer": False,
        "hdfs_bridgs": False,
        "plasma": "deprecated",
        "simd_level": "default",
        "runtime_simd_level": "max",
        "with_backtrace": False,
        "with_boost": "auto",
        "with_brotli": False,
        "with_bz2": False,
        "with_csv": False,
        "with_cuda": False,
        "with_flight_rpc": "auto",
        "with_flight_sql": False,
        "with_gcs": False,
        "with_gflags": "auto",
        "with_jemalloc": "auto",
        "with_mimalloc": False,
        "with_glog": "auto",
        "with_grpc": "auto",
        "with_json": False,
        "with_thrift": "auto",
        "with_llvm": "auto",
        "with_openssl": "auto",
        "with_opentelemetry": False,
        "with_orc": False,
        "with_protobuf": "auto",
        "with_re2": "auto",
        "with_s3": False,
        "with_utf8proc": "auto",
        "with_lz4": False,
        "with_snappy": False,
        "with_zlib": False,
        "with_zstd": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        # arrow >= 10.0.0 requires C++17.
        # https://github.com/apache/arrow/pull/13991
        return "11" if Version(self.version) < "10.0.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "11": {
                "clang": "3.9",
            },
            "17": {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.0.0":
            del self.options.simd_level
            del self.options.runtime_simd_level
        elif Version(self.version) < "6.0.0":
            self.options.simd_level = "sse4_2"
        if Version(self.version) < "6.0.0":
            del self.options.with_gcs
        if Version(self.version) < "7.0.0":
            del self.options.skyhook
            del self.options.with_flight_sql
            del self.options.with_opentelemetry
        if Version(self.version) < "8.0.0":
            del self.options.substrait

        self.options.parquet = self._parquet()
        self.options.compute = self._compute()
        self.options.dataset_modules = self._dataset_modules()
        self.options.with_boost = self._with_boost()
        self.options.with_flight_rpc = self._with_flight_rpc()
        self.options.with_gflags = self._with_gflags()
        self.options.with_glog = self._with_glog()
        self.options.with_grpc = self._with_grpc()
        self.options.with_jemalloc = self._with_jemalloc()
        self.options.with_thrift = self._with_thrift()
        self.options.with_llvm = self._with_llvm()
        self.options.with_openssl = self._with_openssl()
        self.options.with_protobuf = self._with_protobuf()
        self.options.with_re2 = self._with_re2()
        self.options.with_utf8proc = self._with_utf8proc()

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def _compute(self):
        if self.options.compute == "auto":
            return bool(self._parquet() or self._dataset_modules()) or bool(self.options.get_safe("substrait", False))
        else:
            return bool(self.options.compute)

    def _parquet(self):
        if self.options.parquet == "auto":
            return bool(self.options.get_safe("substrait", False))
        else:
            return bool(self.options.parquet)

    def _dataset_modules(self):
        if self.options.dataset_modules == "auto":
            return bool(self.options.get_safe("substrait", False))
        else:
            return bool(self.options.dataset_modules)

    def _with_jemalloc(self):
        if self.options.with_jemalloc == "auto":
            return bool("BSD" in str(self.settings.os))
        else:
            return bool(self.options.with_jemalloc)

    def _with_re2(self):
        if self.options.with_re2 == "auto":
            if self.options.gandiva or self.options.parquet:
                return True
            if Version(self) >= "7.0.0" and (self._compute() or self._dataset_modules()):
                return True
            return False
        else:
            return bool(self.options.with_re2)

    def _with_protobuf(self):
        if self.options.with_protobuf == "auto":
            return bool(self.options.gandiva or self._with_flight_rpc() or self.options.with_orc or self.options.get_safe("substrait", False))
        else:
            return bool(self.options.with_protobuf)

    def _with_flight_rpc(self):
        if self.options.with_flight_rpc == "auto":
            return bool(self.options.get_safe("with_flight_sql", False))
        else:
            return bool(self.options.with_flight_rpc)

    def _with_gflags(self):
        if self.options.with_gflags == "auto":
            return bool(self._with_glog() or self._with_grpc())
        else:
            return bool(self.options.with_gflags)

    def _with_glog(self):
        if self.options.with_glog == "auto":
            return False
        else:
            return bool(self.options.with_glog)

    def _with_grpc(self):
        if self.options.with_grpc == "auto":
            return self._with_flight_rpc()
        else:
            return bool(self.options.with_grpc)

    def _with_boost(self):
        if self.options.with_boost == "auto":
            if self.options.gandiva:
                return True
            version = Version(self.version)
            if version.major == "1":
                if self._parquet() and self.settings.compiler == "gcc" and self.settings.compiler.version < Version("4.9"):
                    return True
            elif version.major >= "2":
                if is_msvc(self):
                    return True
            return False
        else:
            return bool(self.options.with_boost)

    def _with_thrift(self):
        if self.options.with_thrift == "auto":
            return bool(self._parquet())
        else:
            return bool(self.options.with_thrift)

    def _with_utf8proc(self):
        if self.options.with_utf8proc == "auto":
            return bool(self._compute() or self.options.gandiva)
        else:
            return bool(self.options.with_utf8proc)

    def _with_llvm(self):
        if self.options.with_llvm == "auto":
            return bool(self.options.gandiva)
        else:
            return bool(self.options.with_llvm)

    def _with_openssl(self):
        if self.options.with_openssl == "auto":
            return bool(self.options.encryption or self._with_flight_rpc() or self.options.with_s3)
        else:
            return bool(self.options.with_openssl)

    def _requires_rapidjson(self):
        if self.options.with_json:
            return True
        if Version(self.version) >= "7.0.0" and self.options.encryption:
            return True
        return False

    def requirements(self):
        if self.options.with_thrift:
            self.requires("thrift/0.17.0")
        if self.options.with_protobuf:
            self.requires("protobuf/3.21.9")
        if self.options.with_jemalloc:
            self.requires("jemalloc/5.3.0")
        if self.options.with_mimalloc:
            self.requires("mimalloc/1.7.6")
        if self.options.with_boost:
            self.requires("boost/1.82.0")
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_glog:
            self.requires("glog/0.6.0")
        if self.options.get_safe("with_gcs"):
            self.requires("google-cloud-cpp/1.40.1")
        if self.options.with_grpc:
            self.requires("grpc/1.50.0")
        if self._requires_rapidjson():
            self.requires("rapidjson/1.1.0")
        if self.options.with_llvm:
            self.requires("llvm-core/13.0.0")
        if self.options.with_openssl:
            # aws-sdk-cpp requires openssl/1.1.1. it uses deprecated functions in openssl/3.0.0
            if self.options.with_s3:
                self.requires("openssl/1.1.1t")
            else:
                self.requires("openssl/1.1.1t")
        if self.options.get_safe("with_opentelemetry"):
            self.requires("opentelemetry-cpp/1.7.0")
        if self.options.with_s3:
            self.requires("aws-sdk-cpp/1.9.234")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_snappy:
            self.requires("snappy/1.1.9")
        if Version(self.version) >= "6.0.0" and \
            self.options.get_safe("simd_level") != None or \
            self.options.get_safe("runtime_simd_level") != None:
            self.requires("xsimd/9.0.1")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_re2:
            self.requires("re2/20220601")
        if self.options.with_utf8proc:
            self.requires("utf8proc/2.8.0")
        if self.options.with_backtrace:
            self.requires("libbacktrace/cci.20210118")

    def validate(self):
        # validate options with 'auto' as default value
        auto_options = ["parquet", "compute", "dataset_modules", "with_boost", "with_flight_rpc", "with_gflags", "with_glog",
                        "with_grpc", "with_jemalloc", "with_thrift", "with_llvm", "with_openssl", "with_protobuf", "with_re2", "with_utf8proc"]
        for option in auto_options:
            assert "auto" not in str(self.options.get_safe(option)), f"Option '{option}' contains 'auto' value, wich is not allowed. Generally the final value should be True/False"

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.get_safe("skyhook", False):
            raise ConanInvalidConfiguration("CCI has no librados recipe (yet)")
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CCI has no cuda recipe (yet)")
        if self.options.with_orc:
            raise ConanInvalidConfiguration("CCI has no orc recipe (yet)")
        if self.options.with_s3 and not self.dependencies["aws-sdk-cpp"].options.config:
            raise ConanInvalidConfiguration("arrow:with_s3 requires aws-sdk-cpp:config is True.")

        if self.options.shared and self.options.with_jemalloc:
            if self.dependencies["jemalloc"].options.enable_cxx:
                raise ConanInvalidConfiguration("jemmalloc.enable_cxx of a static jemalloc must be disabled")

        if Version(self.version) < "6.0.0" and self.options.get_safe("simd_level") == "default":
            raise ConanInvalidConfiguration(f"In {self.ref}, simd_level options is not supported `default` value.")

    def build_requirements(self):
        if Version(self.version) >= "13.0.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            filename=f"apache-arrow-{self.version}.tar.gz", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if cross_building(self):
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            if cmake_system_processor == "aarch64":
                tc.variables["ARROW_CPU_FLAG"] = "armv8"
        if is_msvc(self):
            tc.variables["ARROW_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["ARROW_DEPENDENCY_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_PACKAGE_KIND"] = "conan" # See https://github.com/conan-io/conan-center-index/pull/14903/files#r1057938314 for details
        tc.variables["ARROW_GANDIVA"] = bool(self.options.gandiva)
        tc.variables["ARROW_PARQUET"] = self.options.parquet
        tc.variables["ARROW_SUBSTRAIT"] = bool(self.options.get_safe("substrait", False))
        tc.variables["ARROW_ACERO"] = bool(self.options.acero)
        tc.variables["ARROW_DATASET"] = self.options.dataset_modules
        tc.variables["ARROW_FILESYSTEM"] = bool(self.options.filesystem_layer)
        tc.variables["PARQUET_REQUIRE_ENCRYPTION"] = bool(self.options.encryption)
        tc.variables["ARROW_HDFS"] = bool(self.options.hdfs_bridgs)
        tc.variables["ARROW_VERBOSE_THIRDPARTY_BUILD"] = True
        tc.variables["ARROW_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["ARROW_BUILD_STATIC"] = not bool(self.options.shared)
        tc.variables["ARROW_NO_DEPRECATED_API"] = not bool(self.options.deprecated)
        tc.variables["ARROW_FLIGHT"] = self.options.with_flight_rpc
        tc.variables["ARROW_FLIGHT_SQL"] = bool(self.options.get_safe("with_flight_sql", False))
        tc.variables["ARROW_COMPUTE"] = self.options.compute
        tc.variables["ARROW_CSV"] = bool(self.options.with_csv)
        tc.variables["ARROW_CUDA"] = bool(self.options.with_cuda)
        tc.variables["ARROW_JEMALLOC"] = self.options.with_jemalloc
        tc.variables["jemalloc_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_MIMALLOC"] = bool(self.options.with_mimalloc)
        tc.variables["ARROW_JSON"] = bool(self.options.with_json)
        tc.variables["google_cloud_cpp_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_GCS"] = bool(self.options.get_safe("with_gcs", False))
        tc.variables["BOOST_SOURCE"] = "SYSTEM"
        tc.variables["Protobuf_SOURCE"] = "SYSTEM"
        if self.options.with_protobuf:
            tc.variables["ARROW_PROTOBUF_USE_SHARED"] = bool(self.dependencies["protobuf"].options.shared)
        tc.variables["gRPC_SOURCE"] = "SYSTEM"
        if self.options.with_grpc:
            tc.variables["ARROW_GRPC_USE_SHARED"] = bool(self.dependencies["grpc"].options.shared)

        tc.variables["ARROW_USE_GLOG"] = self.options.with_glog
        tc.variables["GLOG_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_WITH_BACKTRACE"] = bool(self.options.with_backtrace)
        tc.variables["ARROW_WITH_BROTLI"] = bool(self.options.with_brotli)
        tc.variables["brotli_SOURCE"] = "SYSTEM"
        if self.options.with_brotli:
            tc.variables["ARROW_BROTLI_USE_SHARED"] = bool(self.dependencies["brotli"].options.shared)
        tc.variables["gflags_SOURCE"] = "SYSTEM"
        if self.options.with_gflags:
            tc.variables["ARROW_GFLAGS_USE_SHARED"] = bool(self.dependencies["gflags"].options.shared)
        tc.variables["ARROW_WITH_BZ2"] = bool(self.options.with_bz2)
        tc.variables["BZip2_SOURCE"] = "SYSTEM"
        if self.options.with_bz2:
            tc.variables["ARROW_BZ2_USE_SHARED"] = bool(self.dependencies["bzip2"].options.shared)
        tc.variables["ARROW_WITH_LZ4"] = bool(self.options.with_lz4)
        tc.variables["lz4_SOURCE"] = "SYSTEM"
        if self.options.with_lz4:
            tc.variables["ARROW_LZ4_USE_SHARED"] = bool(self.dependencies["lz4"].options.shared)
        tc.variables["ARROW_WITH_SNAPPY"] = bool(self.options.with_snappy)
        tc.variables["RapidJSON_SOURCE"] = "SYSTEM"
        tc.variables["Snappy_SOURCE"] = "SYSTEM"
        if self.options.with_snappy:
            tc.variables["ARROW_SNAPPY_USE_SHARED"] = bool(self.dependencies["snappy"].options.shared)
        tc.variables["ARROW_WITH_ZLIB"] = bool(self.options.with_zlib)
        tc.variables["re2_SOURCE"] = "SYSTEM"
        tc.variables["ZLIB_SOURCE"] = "SYSTEM"
        tc.variables["xsimd_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_WITH_ZSTD"] = bool(self.options.with_zstd)
        if Version(self.version) >= "2.0":
            tc.variables["zstd_SOURCE"] = "SYSTEM"
            tc.variables["ARROW_SIMD_LEVEL"] = str(self.options.simd_level).upper()
            tc.variables["ARROW_RUNTIME_SIMD_LEVEL"] = str(self.options.runtime_simd_level).upper()
        else:
            tc.variables["ZSTD_SOURCE"] = "SYSTEM"
        if self.options.with_zstd:
            tc.variables["ARROW_ZSTD_USE_SHARED"] = bool(self.dependencies["zstd"].options.shared)
        tc.variables["ORC_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_WITH_THRIFT"] = bool(self.options.with_thrift)
        tc.variables["Thrift_SOURCE"] = "SYSTEM"
        if self.options.with_thrift:
            tc.variables["THRIFT_VERSION"] = bool(self.dependencies["thrift"].ref.version) # a recent thrift does not require boost
            tc.variables["ARROW_THRIFT_USE_SHARED"] = bool(self.dependencies["thrift"].options.shared)
        tc.variables["ARROW_USE_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
            tc.variables["ARROW_OPENSSL_USE_SHARED"] = bool(self.dependencies["openssl"].options.shared)
        if self.options.with_boost:
            tc.variables["ARROW_USE_BOOST"] = True
            tc.variables["ARROW_BOOST_USE_SHARED"] = bool(self.dependencies["boost"].options.shared)
        tc.variables["ARROW_S3"] = bool(self.options.with_s3)
        tc.variables["AWSSDK_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_BUILD_UTILITIES"] = bool(self.options.cli)
        tc.variables["ARROW_BUILD_INTEGRATION"] = False
        tc.variables["ARROW_INSTALL_NAME_RPATH"] = True
        tc.variables["ARROW_BUILD_EXAMPLES"] = False
        tc.variables["ARROW_BUILD_TESTS"] = False
        tc.variables["ARROW_ENABLE_TIMING_TESTS"] = False
        tc.variables["ARROW_BUILD_BENCHMARKS"] = False
        tc.variables["LLVM_SOURCE"] = "SYSTEM"
        tc.variables["ARROW_WITH_UTF8PROC"] = self.options.with_utf8proc
        tc.variables["ARROW_BOOST_REQUIRED"] = self.options.with_boost
        tc.variables["utf8proc_SOURCE"] = "SYSTEM"
        if self.options.with_utf8proc:
            tc.variables["ARROW_UTF8PROC_USE_SHARED"] = bool(self.dependencies["utf8proc"].options.shared)
        tc.variables["BUILD_WARNING_LEVEL"] = "PRODUCTION"
        if is_msvc(self):
            tc.variables["ARROW_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        if self.options.with_llvm:
            tc.variables["LLVM_DIR"] = self.dependencies["llvm-core"].package_folder.replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if "7.0.0" <= Version(self.version) < "10.0.0":
            for filename in glob.glob(os.path.join(self.source_folder, "cpp", "cmake_modules", "Find*.cmake")):
                if os.path.basename(filename) not in [
                    "FindArrow.cmake",
                    "FindArrowAcero.cmake",
                    "FindArrowCUDA.cmake",
                    "FindArrowDataset.cmake",
                    "FindArrowFlight.cmake",
                    "FindArrowFlightSql.cmake",
                    "FindArrowFlightTesting.cmake",
                    "FindArrowPython.cmake",
                    "FindArrowPythonFlight.cmake",
                    "FindArrowSubstrait.cmake",
                    "FindArrowTesting.cmake",
                    "FindGandiva.cmake",
                    "FindParquet.cmake",
                ]:
                    os.remove(filename)

    def build(self):
        self._patch_sources()
        cmake =CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cpp"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="NOTICE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake =CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # FIXME: fix CMake targets of components

        self.cpp_info.set_property("cmake_file_name", "Arrow")

        suffix = "_static" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["libarrow"].set_property("pkg_config_name", "arrow")
        self.cpp_info.components["libarrow"].libs = [f"arrow{suffix}"]
        if not self.options.shared:
            self.cpp_info.components["libarrow"].defines = ["ARROW_STATIC"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libarrow"].system_libs = ["pthread", "m", "dl", "rt"]

        if self.options.parquet:
            self.cpp_info.components["libparquet"].set_property("pkg_config_name", "parquet")
            self.cpp_info.components["libparquet"].libs = [f"parquet{suffix}"]
            self.cpp_info.components["libparquet"].requires = ["libarrow"]
            if not self.options.shared:
                self.cpp_info.components["libparquet"].defines = ["PARQUET_STATIC"]

        if self.options.get_safe("substrait"):
            self.cpp_info.components["libarrow_substrait"].set_property("pkg_config_name", "arrow_substrait")
            self.cpp_info.components["libarrow_substrait"].libs = [f"arrow_substrait{suffix}"]
            self.cpp_info.components["libarrow_substrait"].requires = ["libparquet", "dataset"]

        # Plasma was deprecated in Arrow 12.0.0
        del self.options.plasma

        if self.options.acero:
            self.cpp_info.components["libacero"].libs = [f"arrow_acero{suffix}"]
            self.cpp_info.components["libacero"].names["cmake_find_package"] = "acero"
            self.cpp_info.components["libacero"].names["cmake_find_package_multi"] = "acero"
            self.cpp_info.components["libacero"].names["pkg_config"] = "acero"
            self.cpp_info.components["libacero"].requires = ["libarrow"]

        if self.options.gandiva:
            self.cpp_info.components["libgandiva"].set_property("pkg_config_name", "gandiva")
            self.cpp_info.components["libgandiva"].libs = [f"gandiva{suffix}"]
            self.cpp_info.components["libgandiva"].requires = ["libarrow"]
            if not self.options.shared:
                self.cpp_info.components["libgandiva"].defines = ["GANDIVA_STATIC"]

        if self.options.with_flight_rpc:
            self.cpp_info.components["libarrow_flight"].set_property("pkg_config_name", "flight_rpc")
            self.cpp_info.components["libarrow_flight"].libs = [f"arrow_flight{suffix}"]
            self.cpp_info.components["libarrow_flight"].requires = ["libarrow"]

        if self.options.get_safe("with_flight_sql"):
            self.cpp_info.components["libarrow_flight_sql"].set_property("pkg_config_name", "flight_sql")
            self.cpp_info.components["libarrow_flight_sql"].libs = [f"arrow_flight_sql{suffix}"]
            self.cpp_info.components["libarrow_flight_sql"].requires = ["libarrow", "libarrow_flight"]

        if self.options.dataset_modules:
            self.cpp_info.components["dataset"].libs = ["arrow_dataset"]
            if self.options.parquet:
                self.cpp_info.components["dataset"].requires = ["libparquet"]

        if self.options.cli and (self.options.with_cuda or self.options.with_flight_rpc or self.options.parquet):
            binpath = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH env var: {binpath}")
            self.env_info.PATH.append(binpath)

        if self.options.with_boost:
            if self.options.gandiva:
                # FIXME: only filesystem component is used
                self.cpp_info.components["libgandiva"].requires.append("boost::boost")
            if self.options.parquet and self.settings.compiler == "gcc" and self.settings.compiler.version < Version("4.9"):
                self.cpp_info.components["libparquet"].requires.append("boost::boost")
            if Version(self.version) >= "2.0":
                # FIXME: only headers components is used
                self.cpp_info.components["libarrow"].requires.append("boost::boost")
        if self.options.with_openssl:
            self.cpp_info.components["libarrow"].requires.append("openssl::openssl")
        if self.options.with_gflags:
            self.cpp_info.components["libarrow"].requires.append("gflags::gflags")
        if self.options.with_glog:
            self.cpp_info.components["libarrow"].requires.append("glog::glog")
        if self.options.with_jemalloc:
            self.cpp_info.components["libarrow"].requires.append("jemalloc::jemalloc")
        if self.options.with_mimalloc:
            self.cpp_info.components["libarrow"].requires.append("mimalloc::mimalloc")
        if self.options.with_re2:
            if self.options.gandiva:
                self.cpp_info.components["libgandiva"].requires.append("re2::re2")
            if self.options.parquet:
                self.cpp_info.components["libparquet"].requires.append("re2::re2")
            self.cpp_info.components["libarrow"].requires.append("re2::re2")
        if self.options.with_llvm:
            self.cpp_info.components["libgandiva"].requires.append("llvm-core::llvm-core")
        if self.options.with_protobuf:
            self.cpp_info.components["libarrow"].requires.append("protobuf::protobuf")
        if self.options.with_utf8proc:
            self.cpp_info.components["libarrow"].requires.append("utf8proc::utf8proc")
        if self.options.with_thrift:
            self.cpp_info.components["libarrow"].requires.append("thrift::thrift")
        if self.options.with_backtrace:
            self.cpp_info.components["libarrow"].requires.append("libbacktrace::libbacktrace")
        if self.options.with_cuda:
            self.cpp_info.components["libarrow"].requires.append("cuda::cuda")
        if self._requires_rapidjson():
            self.cpp_info.components["libarrow"].requires.append("rapidjson::rapidjson")
        if self.options.with_s3:
            self.cpp_info.components["libarrow"].requires.append("aws-sdk-cpp::s3")
        if self.options.get_safe("with_gcs"):
            self.cpp_info.components["libarrow"].requires.append("google-cloud-cpp::storage")
        if self.options.with_orc:
            self.cpp_info.components["libarrow"].requires.append("orc::orc")
        if self.options.get_safe("with_opentelemetry"):
            self.cpp_info.components["libarrow"].requires.append("opentelemetry-cpp::opentelemetry-cpp")
        if self.options.with_brotli:
            self.cpp_info.components["libarrow"].requires.append("brotli::brotli")
        if self.options.with_bz2:
            self.cpp_info.components["libarrow"].requires.append("bzip2::bzip2")
        if self.options.with_lz4:
            self.cpp_info.components["libarrow"].requires.append("lz4::lz4")
        if self.options.with_snappy:
            self.cpp_info.components["libarrow"].requires.append("snappy::snappy")
        if self.options.get_safe("simd_level") != None or self.options.get_safe("runtime_simd_level") != None:
            self.cpp_info.components["libarrow"].requires.append("xsimd::xsimd")
        if self.options.with_zlib:
            self.cpp_info.components["libarrow"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["libarrow"].requires.append("zstd::zstd")
        if self.options.with_boost:
            self.cpp_info.components["libarrow"].requires.append("boost::boost")
        if self.options.with_grpc:
            self.cpp_info.components["libarrow"].requires.append("grpc::grpc")
        if self.options.with_flight_rpc:
            self.cpp_info.components["libarrow_flight"].requires.append("protobuf::protobuf")

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "Arrow"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Arrow"
        self.cpp_info.components["libarrow"].names["cmake_find_package"] = "arrow"
        self.cpp_info.components["libarrow"].names["cmake_find_package_multi"] = "arrow"
        if self.options.parquet:
            self.cpp_info.components["libparquet"].names["cmake_find_package"] = "parquet"
            self.cpp_info.components["libparquet"].names["cmake_find_package_multi"] = "parquet"
        if self.options.get_safe("substrait"):
            self.cpp_info.components["libarrow_substrait"].names["cmake_find_package"] = "arrow_substrait"
            self.cpp_info.components["libarrow_substrait"].names["cmake_find_package_multi"] = "arrow_substrait"
        if self.options.gandiva:
            self.cpp_info.components["libgandiva"].names["cmake_find_package"] = "gandiva"
            self.cpp_info.components["libgandiva"].names["cmake_find_package_multi"] = "gandiva"
        if self.options.with_flight_rpc:
            self.cpp_info.components["libarrow_flight"].names["cmake_find_package"] = "flight_rpc"
            self.cpp_info.components["libarrow_flight"].names["cmake_find_package_multi"] = "flight_rpc"
        if self.options.get_safe("with_flight_sql"):
            self.cpp_info.components["libarrow_flight_sql"].names["cmake_find_package"] = "flight_sql"
            self.cpp_info.components["libarrow_flight_sql"].names["cmake_find_package_multi"] = "flight_sql"
        if self.options.cli and (self.options.with_cuda or self.options.with_flight_rpc or self.options.parquet):
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
