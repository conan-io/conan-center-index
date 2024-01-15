from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file, save
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class FollyConan(ConanFile):
    name = "folly"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("facebook", "components", "core", "efficiency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/folly"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse4_2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse4_2": False
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if str(self.settings.arch) not in ["x86", "x86_64"]:
            del self.options.use_sse4_2

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0", transitive_headers=True, transitive_libs=True)
        self.requires("bzip2/1.0.8")
        self.requires("double-conversion/3.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("gflags/2.2.2")
        self.requires("glog/0.6.0", transitive_headers=True, transitive_libs=True)
        self.requires("libevent/2.1.12", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("lz4/1.9.4", transitive_libs=True)
        self.requires("snappy/1.1.10")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5", transitive_libs=True)
        if not is_msvc(self):
            self.requires("libdwarf/20191104")
        self.requires("libsodium/1.0.19")
        self.requires("xz_utils/5.4.5")
        # FIXME: Causing compilation issues on clang: self.requires("jemalloc/5.2.1")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libiberty/9.1.0")
            self.requires("libunwind/1.7.2")
        self.requires("fmt/10.1.1", transitive_headers=True, transitive_libs=True)

    @property
    def _required_boost_components(self):
        return ["context", "filesystem", "program_options", "regex", "system", "thread"]

    @property
    def _required_boost_conan_components(self):
        return [f"boost::{comp}" for comp in self._required_boost_components]
    
    @property
    def _required_boost_cmake_targets(self):
        return [f"Boost::{comp}" for comp in self._required_boost_components]
    
    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_apple_os(self) and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Conan currently requires a 64bit target architecture for Folly on Macos")

        if is_apple_os(self):
            raise ConanInvalidConfiguration("Current recipe doesn't support Macos. Contributions are welcome.")
        
        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture on Windows")

        if (is_apple_os(self) or self.settings.os == "Windows") and self.options.shared:
            raise ConanInvalidConfiguration(f"Folly could not be built on {self.settings.os} as shared library")

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} could not be built on {self.settings.os}. PR's are welcome.")

        if self.settings.compiler == "clang" and self.options.shared:
            raise ConanInvalidConfiguration(f"Folly {self.version} could not be built by clang as a shared library")

        glog = self.dependencies["glog"]
        if self.options.shared and not glog.options.shared:
            raise ConanInvalidConfiguration(f"If Folly is built as shared lib, glog must be a shared lib too.")
        
        boost = self.dependencies["boost"]
        if boost.options.header_only:
            raise ConanInvalidConfiguration("Folly could not be built with a header only Boost")

        miss_boost_required_comp = any(getattr(boost.options, f"without_{boost_comp}", True) for boost_comp in self._required_boost_components)
        if miss_boost_required_comp:
            required_components = ", ".join(self._required_boost_components)
            raise ConanInvalidConfiguration(f"Folly requires these boost components: {required_components}")

        if self.options.get_safe("use_sse4_2") and str(self.settings.arch) not in ['x86', 'x86_64']:
            raise ConanInvalidConfiguration(f"{self.ref} can use the option use_sse4_2 only on x86 and x86_64 archs.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def _cppstd_flag_value(self, cppstd):
        cppstd = str(cppstd)
        if cppstd.startswith("gnu"):
            prefix = "gnu"
            year = cppstd[3:]
        else:
            prefix = "c"
            year = cppstd
        if is_msvc(self):
            prefix = ""
            if year > "17":
                year = "latest"
        return f"{prefix}++{year}"

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["CMAKE_PROJECT_folly_INCLUDE"] = os.path.join(self.source_folder, "conan_deps.cmake")

        if can_run(self):
            for var in ["FOLLY_HAVE_UNALIGNED_ACCESS", "FOLLY_HAVE_LINUX_VDSO", "FOLLY_HAVE_WCHAR_SUPPORT", "HAVE_VSNPRINTF_ERRORS"]:
                tc.variables[f"{var}_EXITCODE"] = "0"
                tc.variables[f"{var}_EXITCODE__TRYRUN_OUTPUT"] = ""

        if self.options.get_safe("use_sse4_2") and str(self.settings.arch) in ["x86", "x86_64"]:
            tc.preprocessor_definitions["FOLLY_SSE"] = "4"
            tc.preprocessor_definitions["FOLLY_SSE_MINOR"] = "2"
            if not is_msvc(self):
                cflags = "-mfma"
            else:
                cflags = "/arch:FMA"
            tc.blocks["cmake_flags_init"].template += (
                f'string(APPEND CMAKE_CXX_FLAGS_INIT " {cflags}")\n'
                f'string(APPEND CMAKE_C_FLAGS_INIT " {cflags}")\n'
            )

        # Folly is not respecting this from the helper https://github.com/conan-io/conan-center-index/pull/15726/files#r1097068754
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor CMAKE_REQUIRED_LIBRARIES in check_include_file_xxx
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0075"] = "NEW"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        # Honor Boost_ROOT set by boost recipe
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0074"] = "NEW"

        cxx_std_value = self._cppstd_flag_value(self.settings.get_safe("compiler.cppstd", self._min_cppstd))
        # 2019.10.21.00 -> either MSVC_ flags or CXX_STD
        if is_msvc(self):
            tc.variables["MSVC_LANGUAGE_VERSION"] = cxx_std_value
            tc.variables["MSVC_ENABLE_ALL_WARNINGS"] = False
            tc.variables["MSVC_USE_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
            tc.preprocessor_definitions["NOMINMAX"] = ""
        else:
            tc.variables["CXX_STD"] = cxx_std_value

        if not self.dependencies["boost"].options.header_only:
            tc.cache_variables["BOOST_LINK_STATIC"] = not self.dependencies["boost"].options.shared

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0074"] = "NEW"  # Honor Boost_ROOT set by boost recipe
        tc.generate()

        deps = CMakeDeps(self)
        # deps.set_property("backtrace", "cmake_file_name", "Backtrace")
        deps.set_property("boost", "cmake_file_name", "Boost")
        deps.set_property("bzip2", "cmake_file_name", "BZip2")
        deps.set_property("double-conversion", "cmake_file_name", "DoubleConversion")
        deps.set_property("fmt", "cmake_file_name", "fmt")
        deps.set_property("gflags", "cmake_file_name", "Gflags")
        deps.set_property("glog", "cmake_file_name", "Glog")
        # deps.set_property("libaio", "cmake_file_name", "LibAIO")
        deps.set_property("libdwarf", "cmake_file_name", "LibDwarf")
        deps.set_property("libevent", "cmake_file_name", "LibEvent")
        deps.set_property("libiberty", "cmake_file_name", "Libiberty")
        deps.set_property("libsodium", "cmake_file_name", "Libsodium")
        deps.set_property("libunwind", "cmake_file_name", "LibUnwind")
        # deps.set_property("liburing", "cmake_file_name", "LibUring")
        deps.set_property("lz4", "cmake_file_name", "LZ4")
        deps.set_property("openssl", "cmake_file_name", "OpenSSL")
        deps.set_property("snappy", "cmake_file_name", "Snappy")
        deps.set_property("xz_utils", "cmake_file_name", "LibLZMA")
        deps.set_property("zlib", "cmake_file_name", "ZLIB")
        deps.set_property("zstd", "cmake_file_name", "Zstd")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        folly_deps = os.path.join(self.source_folder, "CMake", "folly-deps.cmake")
        replace_in_file(self, folly_deps, " MODULE", " ")
        replace_in_file(self, folly_deps, "${Boost_LIBRARIES}", f"{' '.join(self._required_boost_cmake_targets)}")
        replace_in_file(self, folly_deps, "OpenSSL 1.1.1", "OpenSSL")
        # Disable example
        save(self, os.path.join(self.source_folder, "folly", "logging", "example", "CMakeLists.txt"), "")

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
        self.cpp_info.set_property("cmake_file_name", "folly")
        self.cpp_info.set_property("cmake_target_name", "folly::folly")
        self.cpp_info.set_property("pkg_config_name", "libfolly")

        self.cpp_info.components["libfolly"].set_property("cmake_target_name", "Folly::folly")
        self.cpp_info.components["libfolly"].set_property("pkg_config_name", "libfolly")
        self.cpp_info.components["libfolly"].libs = ["folly"]
        self.cpp_info.components["libfolly"].requires = ["fmt::fmt"] + self._required_boost_conan_components + [
            "double-conversion::double-conversion",
            "gflags::gflags",
            "glog::glog",
            "libevent::libevent",
            "lz4::lz4",
            "openssl::openssl",
            "bzip2::bzip2",
            "snappy::snappy",
            "zlib::zlib",
            "zstd::zstd",
            "libsodium::libsodium",
            "xz_utils::xz_utils"
        ]
        if not is_msvc(self):
            self.cpp_info.components["libfolly"].requires.append("libdwarf::libdwarf")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libfolly"].requires.extend(["libiberty::libiberty", "libunwind::libunwind"])
            self.cpp_info.components["libfolly"].system_libs.extend(["pthread", "dl", "rt"])
            self.cpp_info.components["libfolly"].defines.extend(["FOLLY_HAVE_ELF", "FOLLY_HAVE_DWARF"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["libfolly"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])

        if str(self.settings.compiler.libcxx) == "libstdc++" or (
            self.settings.compiler == "apple-clang" and
            Version(self.settings.compiler.version.value) == "9.0" and
            self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.components["libfolly"].system_libs.append("atomic")

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version.value) >= "11.0":
            self.cpp_info.components["libfolly"].system_libs.append("c++abi")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["libfolly"].system_libs.append("stdc++fs")

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["libfolly"].system_libs.append("stdc++fs" if self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] else "c++fs")

        self.cpp_info.components["follybenchmark"].set_property("cmake_target_name", "Folly::follybenchmark")
        self.cpp_info.components["follybenchmark"].set_property("pkg_config_name", "libfollybenchmark")
        self.cpp_info.components["follybenchmark"].libs = ["follybenchmark"]
        self.cpp_info.components["follybenchmark"].requires = ["libfolly"]

        self.cpp_info.components["folly_test_util"].set_property("cmake_target_name", "Folly::folly_test_util")
        self.cpp_info.components["folly_test_util"].set_property("pkg_config_name", "libfolly_test_util")
        self.cpp_info.components["folly_test_util"].libs = ["folly_test_util"]
        self.cpp_info.components["folly_test_util"].requires = ["libfolly"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["folly_exception_tracer_base"].set_property("cmake_target_name", "Folly::folly_exception_tracer_base")
            self.cpp_info.components["folly_exception_tracer_base"].set_property("pkg_config_name", "libfolly_exception_tracer_base")
            self.cpp_info.components["folly_exception_tracer_base"].libs = ["folly_exception_tracer_base"]
            self.cpp_info.components["folly_exception_tracer_base"].requires = ["libfolly"]

            self.cpp_info.components["folly_exception_tracer"].set_property("cmake_target_name", "Folly::folly_exception_tracer")
            self.cpp_info.components["folly_exception_tracer"].set_property("pkg_config_name", "libfolly_exception_tracer")
            self.cpp_info.components["folly_exception_tracer"].libs = ["folly_exception_tracer"]
            self.cpp_info.components["folly_exception_tracer"].requires = ["folly_exception_tracer_base"]

            self.cpp_info.components["folly_exception_counter"].set_property("cmake_target_name", "Folly::folly_exception_counter")
            self.cpp_info.components["folly_exception_counter"].set_property("pkg_config_name", "libfolly_exception_counter")
            self.cpp_info.components["folly_exception_counter"].libs = ["folly_exception_counter"]
            self.cpp_info.components["folly_exception_counter"].requires = ["folly_exception_tracer"]

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "folly"
        self.cpp_info.filenames["cmake_find_package_multi"] = "folly"
        self.cpp_info.names["cmake_find_package"] = "Folly"
        self.cpp_info.names["cmake_find_package_multi"] = "Folly"
        self.cpp_info.names["pkg_config"] = "libfolly"
        self.cpp_info.components["libfolly"].names["cmake_find_package"] = "folly"
        self.cpp_info.components["libfolly"].names["cmake_find_package_multi"] = "folly"

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.components["follybenchmark"].names["cmake_find_package"] = "follybenchmark"
        self.cpp_info.components["follybenchmark"].names["cmake_find_package_multi"] = "follybenchmark"
        self.cpp_info.components["folly_test_util"].names["cmake_find_package"] = "folly_test_util"
        self.cpp_info.components["folly_test_util"].names["cmake_find_package_multi"] = "folly_test_util"

        if self.settings.os in ["Linux", "FreeBSD"]:
            # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
            self.cpp_info.components["folly_exception_tracer_base"].names["cmake_find_package"] = "folly_exception_tracer_base"
            self.cpp_info.components["folly_exception_tracer_base"].names["cmake_find_package_multi"] = "folly_exception_tracer_base"
            self.cpp_info.components["folly_exception_tracer"].names["cmake_find_package"] = "folly_exception_tracer"
            self.cpp_info.components["folly_exception_tracer"].names["cmake_find_package_multi"] = "folly_exception_tracer"
            self.cpp_info.components["folly_exception_counter"].names["cmake_find_package"] = "folly_exception_counter"
            self.cpp_info.components["folly_exception_counter"].names["cmake_find_package_multi"] = "folly_exception_counter"
