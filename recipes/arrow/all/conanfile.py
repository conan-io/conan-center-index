from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class ArrowConan(ConanFile):
    name = "arrow"
    description = "Apache Arrow is a cross-language development platform for in-memory data"
    topics = ("conan", "arrow", "memory")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://arrow.apache.org/"
    license = ("Apache-2.0",)
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "gandiva":  [True, False],
        "parquet": [True, False],
        "plasma": [True, False],
        "cli": [True, False],
        "compute": ["auto", True, False],
        "dataset_modules":  [True, False],
        "deprecated": [True, False],
        "encryption": [True, False],
        "filesystem_layer":  [True, False],
        "hdfs_bridgs": [True, False],
        "with_backtrace": [True, False],
        "with_boost": ["auto", True, False],
        "with_csv": [True, False],
        "with_cuda": [True, False],
        "with_flight_rpc":  [True, False],
        "with_gflags": ["auto", True, False],
        "with_glog": ["auto", True, False],
        "with_grpc": ["auto", True, False],
        "with_hiveserver2": [True, False],
        "with_jemalloc": ["auto", True, False],
        "with_json": [True, False],
        "with_llvm": ["auto", True, False],
        "with_openssl": ["auto", True, False],
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
        "parquet": False,
        "plasma": False,
        "cli": False,
        "compute": "auto",
        "dataset_modules": False,
        "deprecated": True,
        "encryption": False,
        "filesystem_layer": False,
        "hdfs_bridgs": False,
        "with_backtrace": False,
        "with_boost": "auto",
        "with_brotli": False,
        "with_bz2": False,
        "with_csv": False,
        "with_cuda": False,
        "with_flight_rpc": False,
        "with_gflags": "auto",
        "with_jemalloc": "auto",
        "with_glog": "auto",
        "with_grpc": "auto",
        "with_hiveserver2": False,
        "with_json": False,
        "with_llvm": "auto",
        "with_openssl": "auto",
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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "clang" and self.settings.compiler.version <= tools.Version("3.9"):
            raise ConanInvalidConfiguration("This recipe does not support this compiler version")

        if self.options.shared:
            del self.options.fPIC
        if self.options.compute == False and not self._compute(True):
            raise ConanInvalidConfiguration("compute options is required (or choose auto)")
        if self.options.with_jemalloc == False and self._with_jemalloc(True):
            raise ConanInvalidConfiguration("with_jemalloc option is required (or choose auto)")
        if self.options.with_re2 == False and self._with_re2(True):
            raise ConanInvalidConfiguration("with_re2 option is required (or choose auto)")
        if self.options.with_protobuf == False and self._with_protobuf(True):
            raise ConanInvalidConfiguration("with_protobuf option is required (or choose auto)")
        if self.options.with_gflags == False and self._with_gflags(True):
            raise ConanInvalidConfiguration("with_gflags options is required (or choose auto)")
        if self.options.with_grpc == False and self._with_grpc(True):
            raise ConanInvalidConfiguration("with_grpc options is required (or choose auto)")
        if self.options.with_boost == False and self._with_boost(True):
            raise ConanInvalidConfiguration("with_boost options is required (or choose auto)")
        if self.options.with_openssl == False and self._with_openssl(True):
            raise ConanInvalidConfiguration("with_openssl options is required (or choose auto)")
        if self.options.with_llvm == False and self._with_llvm(True):
            raise ConanInvalidConfiguration("with_openssl options is required (or choose auto)")

    def _compute(self, required=False):
        if required or self.options.compute == "auto":
            return bool(self.options.dataset_modules)
        else:
            return bool(self.options.compute)

    def _with_jemalloc(self, required=False):
        if required or self.options.with_jemalloc == "auto":
            return bool("BSD" in str(self.settings.os))
        else:
            return bool(self.options.with_jemalloc)

    def _with_re2(self, required=False):
        if required or self.options.with_re2 == "auto":
            return bool(self.options.gandiva)
        else:
            return bool(self.options.with_re2)

    def _with_protobuf(self, required=False):
        if required or self.options.with_protobuf == "auto":
            return bool(self.options.gandiva or self.options.with_flight_rpc or self.options.with_orc)
        else:
            return bool(self.options.with_protobuf)

    def _with_gflags(self, required=False):
        if required or self.options.with_gflags == "auto":
            return bool(self.options.plasma or self._with_glog() or self._with_grpc())
        else:
            return bool(self.options.with_gflags)

    def _with_glog(self, required=False):
        if required or self.options.with_glog == "auto":
            return False
        else:
            return bool(self.options.with_glog)

    def _with_grpc(self, required=False):
        if required or self.options.with_grpc == "auto":
            return bool(self.options.with_flight_rpc)
        else:
            return bool(self.options.with_grpc)

    def _with_boost(self, required=False):
        if required or self.options.with_boost == "auto":
            if self.options.gandiva:
                return True
            if self.options.parquet and self.settings.compiler == "gcc" and self.settings.compiler.version < tools.Version("4.9"):
                return True
            return False
        else:
            return bool(self.options.with_boost)

    def _with_thrift(self, required=False):
        # No self.options.with_thift exists
        return bool(self.options.with_hiveserver2 or self.options.parquet)

    def _with_utf8proc(self, required=False):
        if required or self.options.with_utf8proc == "auto":
            return False
        else:
            return bool(self.options.with_utf8proc)

    def _with_llvm(self, required=False):
        if required or self.options.with_llvm == "auto":
            return bool(self.options.gandiva)
        else:
            return bool(self.options.with_openssl)

    def _with_openssl(self, required=False):
        if required or self.options.with_openssl == "auto":
            return bool(self.options.encryption or self.options.with_flight_rpc or self.options.with_s3)
        else:
            return bool(self.options.with_openssl)

    def build_requirements(self):
        if self._with_grpc():
            raise ConanInvalidConfiguration("CCI has no grpc recipe (yet)")

    def requirements(self):
        if self._with_thrift():
            self.requires("thrift/0.13.0")
        if self.options.with_backtrace:
            raise ConanInvalidConfiguration("CCI has no backtrace recipe (yet)")
        if self._with_protobuf():
            self.requires("protobuf/3.11.4")
        if self._with_jemalloc():
            self.requires("jemalloc/5.2.1")
        if self._with_boost():
            self.requires("boost/1.72.0")
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CCI has no cuda recipe (yet)")
        if self.options.with_flight_rpc:
            raise ConanInvalidConfiguration("CCI has no flight_rpc recipe (yet)")
        if self._with_gflags():
            self.requires("gflags/2.2.2")
        if self._with_glog():
            self.requires("glog/0.4.0")
        if self.options.with_hiveserver2:
            raise ConanInvalidConfiguration("CCI has no hiveserver2 recipe (yet)")
        if self.options.with_json:
            self.requires("rapidjson/1.1.0")
        if self._with_llvm():
            raise ConanInvalidConfiguration("CCI has no llvm recipe (yet)")
        if self._with_openssl():
            self.requires("openssl/1.1.1g")
        if self.options.with_s3:
            self.requires("aws-sdk-cpp/1.7.299")
        if self.options.with_brotli:
            self.requires("brotli/1.0.7")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_orc:
            raise ConanInvalidConfiguration("CCI has no orc recipe (yet)")
        if self.options.with_lz4:
            self.requires("lz4/1.9.2")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.4.4")
        if self._with_re2():
            self.requires("re2/20200301")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "arrow-apache-arrow-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["ARROW_USE_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)
        self._cmake.definitions["ARROW_DEPENDENCY_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_GANDIVA"] = self.options.gandiva
        self._cmake.definitions["ARROW_PARQUET"] = self.options.parquet
        self._cmake.definitions["ARROW_PLASMA"] = self.options.plasma
        self._cmake.definitions["ARROW_DATASET"] = self.options.dataset_modules
        self._cmake.definitions["ARROW_FILESYSTEM"] = self.options.filesystem_layer
        self._cmake.definitions["PARQUET_REQUIRE_ENCRYPTION"] = self.options.encryption
        self._cmake.definitions["ARROW_HDFS"] = self.options.hdfs_bridgs
        self._cmake.definitions["ARROW_VERBOSE_THIRDPARTY_BUILD"] = True
        self._cmake.definitions["ARROW_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ARROW_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ARROW_NO_DEPRECATED_API"] = not self.options.deprecated
        self._cmake.definitions["ARROW_FLIGHT"] = self.options.with_flight_rpc
        self._cmake.definitions["ARROW_HIVESERVER2"] = self.options.with_hiveserver2
        self._cmake.definitions["ARROW_COMPUTE"] = self._compute()
        self._cmake.definitions["ARROW_CSV"] = self.options.with_csv
        self._cmake.definitions["ARROW_CUDA"] = self.options.with_cuda
        self._cmake.definitions["ARROW_JEMALLOC"] = self._with_jemalloc()
        self._cmake.definitions["ARROW_JSON"] = self.options.with_json

        # self._cmake.definitions["ARROW_BOOST_VENDORED"] = False
        self._cmake.definitions["BOOST_SOURCE"] = "SYSTEM"
        self._cmake.definitions["Protobuf_SOURCE"] = "SYSTEM"
        self._cmake.definitions["gRPC_SOURCE"] = "SYSTEM"
        if self._with_protobuf():
            self._cmake.definitions["ARROW_PROTOBUF_USE_SHARED"] = self.options["protobuf"].shared
        self._cmake.definitions["ARROW_HDFS"] = self.options.hdfs_bridgs
        self._cmake.definitions["ARROW_USE_GLOG"] = self._with_glog()
        self._cmake.definitions["GLOG_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_BACKTRACE"] = self.options.with_backtrace
        self._cmake.definitions["ARROW_WITH_BROTLI"] = self.options.with_brotli
        self._cmake.definitions["Brotli_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_BROTLI_USE_SHARED"] = "brotli" in self.options and not self.options["brotli"].shared
        self._cmake.definitions["gflags_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_BZ2"] = self.options.with_bz2
        self._cmake.definitions["BZip2_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_LZ4"] = self.options.with_lz4
        self._cmake.definitions["Lz4_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_SNAPPY"] = self.options.with_snappy
        self._cmake.definitions["Snappy_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["RE2_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ZLIB_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["ZSTD_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ORC_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_THRIFT"] = self._with_thrift()
        self._cmake.definitions["Thrift_SOURCE"] = "SYSTEM"
        self._cmake.definitions["THRIFT_VERSION"] = "1.0"  # a recent thrift does not require boost
        self._cmake.definitions["ARROW_USE_OPENSSL"] = self._with_openssl()
        if self._with_openssl():
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        if self._with_boost():
            self._cmake.definitions["ARROW_BOOST_USE_SHARED"] = self.options["boost"].shared
        self._cmake.definitions["ARROW_S3"] = self.options.with_s3
        self._cmake.definitions["AWSSDK_SOURCE"] = "SYSTEM"

        self._cmake.definitions["ARROW_BUILD_UTILITIES"] = self.options.cli
        self._cmake.definitions["ARROW_BUILD_INTEGRATION"] = False
        self._cmake.definitions["ARROW_INSTALL_NAME_RPATH"] = False
        self._cmake.definitions["ARROW_BUILD_EXAMPLES"] = False
        self._cmake.definitions["ARROW_BUILD_TESTS"] = False
        self._cmake.definitions["ARROW_ENABLE_TIMING_TESTS"] = False
        self._cmake.definitions["ARROW_BUILD_BENCHMARKS"] = False

        self._cmake.definitions["LLVM_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_UTF8PROC"] = self._with_utf8proc()
        self._cmake.definitions["utf8proc_SOURCE"] = "SYSTEM"

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["ARROW_USE_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)

        if self._with_llvm():
            self._cmake.definitions["LLVM_DIR"] = self.deps_cpp_info["llvm"].rootpath.replace("\\", "/")

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        if self.options.shared and self._with_jemalloc():
            if self.options["jemalloc"].enable_cxx:
                raise ConanInvalidConfiguration("jemmalloc.enable_cxx of a static jemalloc must be disabled")

        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("NOTICE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def _lib_name(self, name):
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            return "{}_static".format(name)
        else:
            return "{}".format(name)

    def package_id(self):
        self.options.with_jemalloc = self._with_jemalloc()
        self.info.options.with_gflags = self._with_gflags()
        self.info.options.with_protobuf = self._with_protobuf()
        self.info.options.with_re2 = self._with_re2()
        self.info.options.with_jemalloc = self._with_jemalloc()
        self.info.options.with_openssl = self._with_openssl()
        self.info.options.with_boost = self._with_boost()
        self.info.options.with_glog = self._with_glog()
        self.info.options.with_grpc = self._with_grpc()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Arrow"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Arrow"
        self.cpp_info.components["libarrow"].libs = [self._lib_name("arrow")]
        self.cpp_info.components["libarrow"].names["cmake_find_package"] = "arrow"
        self.cpp_info.components["libarrow"].names["cmake_find_package_multi"] = "arrow"
        self.cpp_info.components["libarrow"].names["pkg_config"] = "arrow"
        if not self.options.shared:
            self.cpp_info.components["libarrow"].defines = ["ARROW_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libarrow"].system_libs = ["pthread"]

        if self.options.parquet:
            self.cpp_info.components["libparquet"].libs = [self._lib_name("parquet")]
            self.cpp_info.components["libparquet"].names["cmake_find_package"] = "parquet"
            self.cpp_info.components["libparquet"].names["cmake_find_package_multi"] = "parquet"
            self.cpp_info.components["libparquet"].names["pkg_config"] = "parquet"
            self.cpp_info.components["libparquet"].requires = ["libarrow"]

        if self.options.plasma:
            self.cpp_info.components["libplasma"].libs = [self._lib_name("plasma")]
            self.cpp_info.components["libplasma"].names["cmake_find_package"] = "plasma"
            self.cpp_info.components["libplasma"].names["cmake_find_package_multi"] = "plasma"
            self.cpp_info.components["libplasma"].names["pkg_config"] = "plasma"
            self.cpp_info.components["libplasma"].requires = ["libarrow"]

        if self.options.gandiva:
            self.cpp_info.components["libgandiva"].libs = [self._lib_name("gandiva")]
            self.cpp_info.components["libgandiva"].names["cmake_find_package"] = "gandiva"
            self.cpp_info.components["libgandiva"].names["cmake_find_package_multi"] = "gandiva"
            self.cpp_info.components["libgandiva"].names["pkg_config"] = "gandiva"
            self.cpp_info.components["libgandiva"].requires = ["libarrow"]

        if self.options.dataset_modules:
            self.cpp_info.components["dataset"].libs = ["arrow_dataset"]

        if self.options.cli:
            binpath = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var: {}".format(binpath))
            self.env_info.PATH.append(binpath)

        if self._with_boost():
            if self.options.gandiva:
                # FIXME: only filesystem component is used
                self.cpp_info.components["libgandiva"].requires.append("boost::boost")
            if self.options.parquet and self.settings.compiler == "gcc" and self.settings.compiler.version < tools.Version("4.9"):
                self.cpp_info.components["libparquet"].requires.append("boost::boost")
        if self._with_openssl():
            self.cpp_info.components["libarrow"].requires.append("openssl::openssl")
        if self._with_gflags():
            self.cpp_info.components["libarrow"].requires.append("gflags::gflags")
        if self._with_glog():
            self.cpp_info.components["libarrow"].requires.append("glog::glog")
        if self._with_jemalloc():
            self.cpp_info.components["libarrow"].requires.append("jemalloc::jemalloc")
        if self._with_re2():
            self.cpp_info.components["libgandiva"].requires.append("re2::re2")
        if self._with_protobuf():
            self.cpp_info.components["libarrow"].requires.append("protobuf::protobuf")
        if self._with_utf8proc():
            self.cpp_info.components["libarrow"].requires.append("uff8proc::uff8proc")
        if self._with_llvm():
            self.cpp_info.components["libarrow"].requires.append("llvm::llvm")
        if self._with_thrift():
            self.cpp_info.components["libarrow"].requires.append("thrift::thrift")

        if self.options.with_backtrace:
            self.cpp_info.components["libarrow"].requires.append("backtrace::backtrace")
        if self.options.with_cuda:
            self.cpp_info.components["libarrow"].requires.append("cuda::cuda")
        if self.options.with_flight_rpc:
            self.cpp_info.components["libarrow"].requires.append("flight::flight")
        if self.options.with_hiveserver2:
            self.cpp_info.components["libarrow"].requires.append("hiveserver2::hiveserver2")
        if self.options.with_json:
            self.cpp_info.components["libarrow"].requires.append("rapidjson::rapidjson")
        if self.options.with_s3:
            self.cpp_info.components["libarrow"].requires.append("aws-sdk-cpp::filesystem")
        if self.options.with_orc:
            self.cpp_info.components["libarrow"].requires.append("orc::orc")
        if self.options.with_brotli:
            self.cpp_info.components["libarrow"].requires.append("brotli::brotli")
        if self.options.with_bz2:
            self.cpp_info.components["libarrow"].requires.append("bz2::bz2")
        if self.options.with_lz4:
            self.cpp_info.components["libarrow"].requires.append("lz4::lz4")
        if self.options.with_snappy:
            self.cpp_info.components["libarrow"].requires.append("snappy::snappy")
        if self.options.with_zlib:
            self.cpp_info.components["libarrow"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["libarrow"].requires.append("zstd::zstd")
