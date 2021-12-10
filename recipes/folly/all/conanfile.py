import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.32.0"


class FollyConan(ConanFile):
    name = "folly"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("folly", "facebook", "components", "core", "efficiency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/folly"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    # Freeze CMake version below 3.17.0 to fix the Linux build
    def build_requirements(self):
        self.build_requires("cmake/3.16.9")

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("bzip2/1.0.8")
        self.requires("double-conversion/3.1.5")
        self.requires("gflags/2.2.2")
        self.requires("glog/0.4.0")
        self.requires("libevent/2.1.12")
        self.requires("lz4/1.9.3")
        self.requires("openssl/1.1.1l")
        self.requires("snappy/1.1.8")
        self.requires("zlib/1.2.11")
        self.requires("zstd/1.4.9")
        self.requires("libdwarf/20191104")
        self.requires("libsodium/1.0.18")
        self.requires("xz_utils/5.2.5")
        # FIXME: Causing compilation issues on clang: self.requires("jemalloc/5.2.1")
        if self.settings.os == "Linux":
            self.requires("libiberty/9.1.0")
            self.requires("libunwind/1.5.0")
        if Version(self.version) >= "2020.08.10.00":
            self.requires("fmt/7.0.3")

    @property
    def _required_boost_components(self):
        return ["context", "filesystem", "program_options", "regex", "system", "thread"]

    def validate(self):
        if tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-compilation not yet supported. Contributions are welcome")
            
        if self.options["boost"].header_only:
            raise ConanInvalidConfiguration("Folly could not be built with a header only Boost")

        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if miss_boost_required_comp:
            raise ConanInvalidConfiguration("Folly requires these boost components: {}".format(", ".join(self._required_boost_components)))
            
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture on Windows")

        if self.settings.os in ["Macos", "Windows"] and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built on {} as shared library".format(self.settings.os))

        if self.version == "2020.08.10.00" and self.settings.compiler == "clang" and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built by clang as a shared library")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
            self._cmake.definitions["CXX_STD"] = self.settings.compiler.get_safe("cppstd") or "c++14"
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["MSVC_ENABLE_ALL_WARNINGS"] = False
                self._cmake.definitions["MSVC_USE_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
            self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "folly"
        self.cpp_info.filenames["cmake_find_package_multi"] = "folly"
        self.cpp_info.names["cmake_find_package"] = "Folly"
        self.cpp_info.names["cmake_find_package_multi"] = "Folly"
        self.cpp_info.names["pkg_config"] = "libfolly"
        self.cpp_info.components["libfolly"].names["cmake_find_package"] = "folly"
        self.cpp_info.components["libfolly"].names["cmake_find_package_multi"] = "folly"
        self.cpp_info.components["libfolly"].names["pkg_config"] = "libfolly"

        if Version(self.version) == "2019.10.21.00":
            self.cpp_info.components["libfolly"].libs = [
                "follybenchmark",
                "folly_test_util",
                "folly"
            ]
        if Version(self.version) == "2020.08.10.00":
            if self.settings.os == "Linux":
                self.cpp_info.components["libfolly"].libs = [
                    "folly_exception_counter",
                    "folly_exception_tracer",
                    "folly_exception_tracer_base",
                    "folly_test_util",
                    "follybenchmark",
                    "folly"
                ]
            else:
                self.cpp_info.components["libfolly"].libs = [
                    "folly_test_util",
                    "follybenchmark",
                    "folly"
                ]
        self.cpp_info.components["libfolly"].requires = [
            "boost::boost",
            "bzip2::bzip2",
            "double-conversion::double-conversion",
            "gflags::gflags",
            "glog::glog",
            "libevent::libevent",
            "lz4::lz4",
            "openssl::openssl",
            "snappy::snappy",
            "zlib::zlib",
            "zstd::zstd",
            "libdwarf::libdwarf",
            "libsodium::libsodium",
            "xz_utils::xz_utils"
        ]
        if self.settings.os == "Linux":
            self.cpp_info.components["libfolly"].requires.extend(["libiberty::libiberty", "libunwind::libunwind"])
            self.cpp_info.components["libfolly"].system_libs.extend(["pthread", "dl", "rt"])

        if Version(self.version) >= "2020.08.10.00":
            self.cpp_info.components["libfolly"].requires.append("fmt::fmt")
            if self.settings.os == "Linux":
                self.cpp_info.components["libfolly"].defines.append("FOLLY_HAVE_ELF")

        elif self.settings.os == "Windows":
            self.cpp_info.components["libfolly"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])

        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
            self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
            Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.components["libfolly"].system_libs.append("atomic")
