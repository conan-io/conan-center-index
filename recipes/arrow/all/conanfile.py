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
        "with_jemalloc": ["auto", True, False],
        "with_deprecated": [True, False],
        "with_cli": [True, False],
        "with_compute": [True, False],
        "with_csv": [True, False],
        "with_cuda": [True, False],
        "with_hdfs_bridge": [True, False],
        "with_dataset_modules":  [True, False],
        "with_filesystem_layer":  [True, False],
        "with_flight_rpc":  [True, False],
        "with_gandiva":  [True, False],
        "with_glog": [True, False],
        "with_backtrace": [True, False],
        "with_json": [True, False],
        "with_openssl": [True, False],
        "with_parquet": [True, False],
        "with_s3": [True, False],
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
        "with_jemalloc": "auto",
        "with_deprecated": True,
        "with_cli": False,
        "with_compute": False,
        "with_csv": False,
        "with_cuda": False,
        "with_hdfs_bridge": False,
        "with_dataset_modules": False,
        "with_filesystem_layer": False,
        "with_flight_rpc": False,
        "with_gandiva": False,
        "with_glog": False,
        "with_backtrace": False,
        "with_json": False,
        "with_openssl": True,
        "with_parquet": False,
        "with_s3": False,
        "with_brotli": False,
        "with_bz2": False,
        "with_lz4": False,
        "with_snappy": False,
        "with_zlib": False,
        "with_zstd": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _with_jemalloc(self):
        if self.options.with_jemalloc != "auto":
            return self.options.with_jemalloc
        return "BSD" in str(self.settings.os)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_dataset_modules and not self.options.with_compute:
            raise ConanInvalidConfiguration("'with_dataset_modules' options requires 'with_compute'")

    @property
    def _boost_required(self):
        return self.options.with_hdfs_bridge or self.options.with_gandiva

    def build_requirements(self):
        if self.options.with_parquet:
            raise ConanInvalidConfiguration("CCI has no thrift recipe (yet)")
            self.requires("thrift/x.y.z")

    def requirements(self):
        self.requires("protobuf/3.11.4")
        if self._with_jemalloc:
            self.requires("jemalloc/5.2.1")
        if self._boost_required:
            self.requires("boost/1.72.0")
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CCI has no cuda recipe (yet)")
            self.requires("cuda/x.y.z")
        if self.options.with_flight_rpc:
            raise ConanInvalidConfiguration("CCI has no grpc recipe (yet)")
            self.requires("grpc/x.y.z")
        if self.options.with_backtrace or self.options.with_gandiva:
            raise ConanInvalidConfiguration("CCI has no llvm recipe (yet)")
            self.requires("llvm/x.y.z")
        if self.options.with_gandiva:
            self.requires("re2/20200301")
        if self.options.with_glog:
            self.requires("glog/0.4.0")
        if self.options.with_json:
            self.requires("rapidjson/1.1.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1g")
        if self.options.with_s3:
            self.requires("aws-sdk-cpp/1.7.299")
        if self.options.with_brotli:
            self.requires("brotli/1.0.7")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lz4:
            self.requires("lz4/1.9.2")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_zstd:
            self.requires("zstd/1.4.4")

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
        self._cmake.definitions["ARROW_VERBOSE_THIRDPARTY_BUILD"] = True
        self._cmake.definitions["ARROW_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ARROW_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ARROW_NO_DEPRECATED_API"] = not self.options.with_deprecated
        self._cmake.definitions["ARROW_HDFS"] = self.options.with_hdfs_bridge
        self._cmake.definitions["ARROW_DATASET"] = self.options.with_dataset_modules
        self._cmake.definitions["ARROW_FILESYSTEM"] = self.options.with_filesystem_layer
        self._cmake.definitions["ARROW_FLIGHT"] = self.options.with_flight_rpc
        self._cmake.definitions["ARROW_GANDIVA"] = self.options.with_gandiva
        self._cmake.definitions["ARROW_COMPUTE"] = self.options.with_compute
        self._cmake.definitions["ARROW_CSV"] = self.options.with_csv
        self._cmake.definitions["ARROW_CUDA"] = self.options.with_cuda
        self._cmake.definitions["ARROW_JEMALLOC"] = self._with_jemalloc
        self._cmake.definitions["ARROW_JSON"] = self.options.with_json
        self._cmake.definitions["ARROW_PARQUET"] = self.options.with_parquet

        # self._cmake.definitions["ARROW_BOOST_VENDORED"] = False
        self._cmake.definitions["BOOST_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_PROTOBUF_USE_SHARED"] = self.options["protobuf"].shared
        self._cmake.definitions["ARROW_HDFS"] = self.options.with_hdfs_bridge
        self._cmake.definitions["ARROW_USE_GLOG"] = self.options.with_glog
        self._cmake.definitions["GLOG_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_BACKTRACE"] = self.options.with_backtrace
        self._cmake.definitions["ARROW_WITH_BROTLI"] = self.options.with_brotli
        self._cmake.definitions["Brotli_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_BZ2"] = self.options.with_bz2
        self._cmake.definitions["BZip2_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_LZ4"] = self.options.with_lz4
        self._cmake.definitions["Lz4_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_SNAPPY"] = self.options.with_snappy
        self._cmake.definitions["Snappy_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["ZLIB_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_WITH_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["ZSTD_SOURCE"] = "SYSTEM"
        self._cmake.definitions["ARROW_USE_OPENSSL"] = self.options.with_openssl
        if self.options.with_openssl:
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        self._cmake.definitions["ARROW_BOOST_USE_SHARED"] = self._boost_required and self.options["boost"].shared
        self._cmake.definitions["ARROW_S3"] = self.options.with_s3
        self._cmake.definitions["AWSSDK_SOURCE"] = "SYSTEM"

        self._cmake.definitions["ARROW_BUILD_UTILITIES"] = self.options.with_cli
        self._cmake.definitions["ARROW_BUILD_INTEGRATION"] = False
        self._cmake.definitions["ARROW_INSTALL_NAME_RPATH"] = False
        self._cmake.definitions["ARROW_BUILD_EXAMPLES"] = False
        self._cmake.definitions["ARROW_BUILD_TESTS"] = False
        self._cmake.definitions["ARROW_ENABLE_TIMING_TESTS"] = False
        self._cmake.definitions["ARROW_BUILD_BENCHMARKS"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["ARROW_USE_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        if self.options.shared and self._with_jemalloc:
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

    def package_id(self):
        self.options.with_jemalloc = self._with_jemalloc

    @property
    def _libs(self):
        libs = []
        if self.options.with_dataset_modules:
            libs.append("arrow_dataset")
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            libs.append("arrow_static")
        else:
            libs.append("arrow")
        return libs

    def package_info(self):
        self.cpp_info.libs = self._libs
        if not self.options.shared:
            self.cpp_info.defines = ["ARROW_STATIC"]

        self.cpp_info.names["cmake_find_package"] = "Arrow"
        self.cpp_info.names["cmake_find_package_multi"] = "Arrow"

        if self.options.with_cli:
            binpath = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var: {}".format(binpath))
            self.env_info.PATH.append(binpath)
