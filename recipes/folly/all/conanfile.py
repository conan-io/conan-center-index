from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.build import can_run
from conan.tools.scm import Version
from conan.tools import files
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class FollyConan(ConanFile):
    name = "folly"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("facebook", "components", "core", "efficiency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/folly"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17 if Version(self.version) >= "2022.01.31.00" else 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8",
        } if self._minimum_cpp_standard == 14 else {
            "gcc": "7",
            "Visual Studio": "16",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("bzip2/1.0.8")
        self.requires("double-conversion/3.2.0")
        self.requires("gflags/2.2.2")
        self.requires("glog/0.4.0")
        self.requires("libevent/2.1.12")
        self.requires("openssl/1.1.1q")
        self.requires("lz4/1.9.3")
        self.requires("snappy/1.1.9")
        self.requires("zlib/1.2.12")
        self.requires("zstd/1.5.2")
        if not is_msvc(self):
            self.requires("libdwarf/20191104")
        self.requires("libsodium/1.0.18")
        self.requires("xz_utils/5.2.5")
        # FIXME: Causing compilation issues on clang: self.requires("jemalloc/5.2.1")
        if self.settings.os == "Linux":
            self.requires("libiberty/9.1.0")
            self.requires("libunwind/1.5.0")
        if Version(self.version) >= "2020.08.10.00":
            self.requires("fmt/7.1.3")

    @property
    def _required_boost_components(self):
        return ["context", "filesystem", "program_options", "regex", "system", "thread"]

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

        if self.version < "2022.01.31.00" and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Conan support for non-Linux platforms starts with Folly version 2022.01.31.00")

        if self.settings.os == "Macos" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Conan currently requires a 64bit target architecture for Folly on Macos")

        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture on Windows")

        if self.settings.os in ["Macos", "Windows"] and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built on {} as shared library".format(self.settings.os))

        if self.version == "2020.08.10.00" and self.settings.compiler == "clang" and self.options.shared:
            raise ConanInvalidConfiguration("Folly could not be built by clang as a shared library")

        if self.options["boost"].header_only:
            raise ConanInvalidConfiguration("Folly could not be built with a header only Boost")

        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if miss_boost_required_comp:
            raise ConanInvalidConfiguration("Folly requires these boost components: {}".format(", ".join(self._required_boost_components)))

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    # FIXME: Freeze max. CMake version at 3.16.2 to fix the Linux build
    def build_requirements(self):
        self.build_requires("cmake/3.16.9")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if can_run(self):
            cmake.definitions["FOLLY_HAVE_UNALIGNED_ACCESS_EXITCODE"] = "0"
            cmake.definitions["FOLLY_HAVE_UNALIGNED_ACCESS_EXITCODE__TRYRUN_OUTPUT"] = ""
            cmake.definitions["FOLLY_HAVE_LINUX_VDSO_EXITCODE"] = "0"
            cmake.definitions["FOLLY_HAVE_LINUX_VDSO_EXITCODE__TRYRUN_OUTPUT"] = ""
            cmake.definitions["FOLLY_HAVE_WCHAR_SUPPORT_EXITCODE"] = "0"
            cmake.definitions["FOLLY_HAVE_WCHAR_SUPPORT_EXITCODE__TRYRUN_OUTPUT"] = ""
            cmake.definitions["HAVE_VSNPRINTF_ERRORS_EXITCODE"] = "0"
            cmake.definitions["HAVE_VSNPRINTF_ERRORS_EXITCODE__TRYRUN_OUTPUT"] = ""
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

        cxx_std_flag = tools.cppstd_flag(self.settings)
        cxx_std_value = cxx_std_flag.split('=')[1] if cxx_std_flag else "c++{}".format(self._minimum_cpp_standard)
        cmake.definitions["CXX_STD"] = cxx_std_value
        if is_msvc:
            cmake.definitions["MSVC_LANGUAGE_VERSION"] = cxx_std_value
            cmake.definitions["MSVC_ENABLE_ALL_WARNINGS"] = False
            cmake.definitions["MSVC_USE_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "folly")
        self.cpp_info.set_property("cmake_target_name", "Folly::folly")
        self.cpp_info.set_property("pkg_config_name", "libfolly")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if Version(self.version) == "2019.10.21.00":
            self.cpp_info.components["libfolly"].libs = [
                "follybenchmark",
                "folly_test_util",
                "folly"
            ]
        elif Version(self.version) >= "2020.08.10.00":
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
            "libsodium::libsodium",
            "xz_utils::xz_utils"
        ]
        if not is_msvc(self):
            self.cpp_info.components["libfolly"].requires.append("libdwarf::libdwarf")
        if self.settings.os == "Linux":
            self.cpp_info.components["libfolly"].requires.extend(["libiberty::libiberty", "libunwind::libunwind"])
            self.cpp_info.components["libfolly"].system_libs.extend(["pthread", "dl", "rt"])

        if Version(self.version) >= "2020.08.10.00":
            self.cpp_info.components["libfolly"].requires.append("fmt::fmt")
            if self.settings.os == "Linux":
                self.cpp_info.components["libfolly"].defines.extend(["FOLLY_HAVE_ELF", "FOLLY_HAVE_DWARF"])

        elif self.settings.os == "Windows":
            self.cpp_info.components["libfolly"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])

        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
            self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
            Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.components["libfolly"].system_libs.append("atomic")

        if self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version.value) >= "11.0":
            self.cpp_info.components["libfolly"].system_libs.append("c++abi")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "folly"
        self.cpp_info.filenames["cmake_find_package_multi"] = "folly"
        self.cpp_info.names["cmake_find_package"] = "Folly"
        self.cpp_info.names["cmake_find_package_multi"] = "Folly"
        self.cpp_info.names["pkg_config"] = "libfolly"
        self.cpp_info.components["libfolly"].names["cmake_find_package"] = "folly"
        self.cpp_info.components["libfolly"].names["cmake_find_package_multi"] = "folly"
        self.cpp_info.components["libfolly"].set_property("cmake_target_name", "Folly::folly")
        self.cpp_info.components["libfolly"].set_property("pkg_config_name", "libfolly")
