from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (get, copy, rmdir, replace_in_file, save, rm,
                               export_conandata_patches, apply_conandata_patches)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=2.1"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            # Folly does not support shared library on Windows: https://github.com/facebook/folly/issues/962
            self.package_type = "static-library"
            del self.options.shared

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.91.0", transitive_headers=True, transitive_libs=True)
        self.requires("bzip2/1.0.8")
        self.requires("fast_float/[>=8.2.10 <9]")
        self.requires("gflags/[>=2.2.2 <3]")
        self.requires("glog/0.7.1", transitive_headers=True, transitive_libs=True)
        self.requires("libevent/2.1.12", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("lz4/1.10.0", transitive_libs=True)
        self.requires("snappy/1.2.1")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/[~1.5]", transitive_libs=True)
        if not is_msvc(self):
            self.requires("libdwarf/0.9.1")
        self.requires("libsodium/[~1.0.20]")
        self.requires("xz_utils/[>=5.4.5 <6]")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libiberty/9.1.0")
            self.requires("libunwind/[>=1.8.0 <2]")
            if self.settings.os == "Linux":
                self.requires("liburing/[>=2.15 <3]")
                self.requires("libaio/0.3.113")
        # MSVC-fmt weirdness was fixed with fmt 11.1 and/or folly 2024.10.07.00
        # # https://github.com/facebook/folly/commit/1cc9a3aeb8099104ba0297601d3e56b6e61e2f96
        self.requires("fmt/[>=11.2.0 <12]", transitive_headers=True, transitive_libs=True)

    @property
    def _required_boost_components(self):
        cmps = ["context", "filesystem", "program_options", "regex"]
        if self.settings.os == "Windows":
            cmps.append("thread")
        return cmps

    def validate(self):
        check_min_cppstd(self, 20)

        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.ref} Folly requires a 64bit target architecture on Windows.")

        boost = self.dependencies["boost"]
        if boost.options.header_only:
            raise ConanInvalidConfiguration("Could not be built with a header only Boost. Use -o 'boost/*:header_only=False'")
        for boost_comp in self._required_boost_components:
            if boost.options.get_safe(f"without_{boost_comp}"):
                raise ConanInvalidConfiguration(f"Required Boost component: {boost_comp}. Pass '-o boost/*:without_{boost_comp}=False'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)
        apply_conandata_patches(self)
        # Skip generating .pc file to avoid Windows errors when trying to compile with pkg-config
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "gen_pkgconfig_vars(FOLLY_PKGCONFIG folly_deps)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        # Folly fails to check Gflags: https://github.com/conan-io/conan/issues/12012
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)

        if (is_apple_os(self) or self.settings.os == "Linux") and cross_building(self):
            # Fix cross-compilation failure on arm64-[macos|linux]
            # CMake Error: try_run() invoked in cross-compiling mode
            # Presetting only the *_EXITCODE cache vars is not enough: check_cxx_source_runs()
            # still calls try_run() unconditionally, and on some toolchains (e.g. CCI's pinned
            # Xcode when cross-building x86_64 on an arm64 host) try_run() actually executes the
            # test binary instead of honoring the cached exit code, so it can still abort the
            # configure. Presetting the check's result variable itself makes check_cxx_source_runs()
            # skip try_run() entirely.
            for check_var in (
                "FOLLY_HAVE_UNALIGNED_ACCESS",
                "FOLLY_HAVE_WEAK_SYMBOLS_EXITCODE",
                "FOLLY_HAVE_LINUX_VDSO",
                "FOLLY_HAVE_WCHAR_SUPPORT",
                "HAVE_VSNPRINTF_ERRORS",
            ):
                tc.cache_variables[check_var] = 1
                tc.cache_variables[f"{check_var}_EXITCODE"] = 0

        if is_msvc(self):
            cxx_std_value = "c++latest" if str(self.settings.compiler.cppstd) > "20" else f"c++20"
            tc.cache_variables["MSVC_LANGUAGE_VERSION"] = cxx_std_value
            tc.cache_variables["MSVC_ENABLE_ALL_WARNINGS"] = False
            tc.cache_variables["MSVC_USE_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
            tc.preprocessor_definitions["NOMINMAX"] = ""

        if not self.dependencies["boost"].options.header_only:
            tc.cache_variables["BOOST_LINK_STATIC"] = not self.dependencies["boost"].options.shared
        tc.generate()

        deps = CMakeDeps(self)
        # CMake file names
        deps.set_property("gflags", "cmake_file_name", "Gflags")
        deps.set_property("glog", "cmake_file_name", "Glog")
        deps.set_property("libdwarf", "cmake_file_name", "LibDwarf")
        deps.set_property("libevent", "cmake_file_name", "LibEvent")
        deps.set_property("libiberty", "cmake_file_name", "Libiberty")
        deps.set_property("libsodium", "cmake_file_name", "Libsodium")
        deps.set_property("libunwind", "cmake_file_name", "LibUnwind")
        deps.set_property("liburing", "cmake_file_name", "LibUring")
        deps.set_property("libaio", "cmake_file_name", "LibAIO")
        deps.set_property("lz4", "cmake_file_name", "LZ4")
        deps.set_property("zstd", "cmake_file_name", "Zstd")
        # CMake additional prefixes
        deps.set_property("bzip2", "cmake_additional_variables_prefixes", ["BZIP2"])
        deps.set_property("fast_float", "cmake_additional_variables_prefixes", ["FASTFLOAT"])
        deps.set_property("fmt", "cmake_additional_variables_prefixes", ["FMT"])
        deps.set_property("gflags", "cmake_additional_variables_prefixes", ["GFLAGS"])
        deps.set_property("glog", "cmake_additional_variables_prefixes", ["GLOG"])
        deps.set_property("libdwarf", "cmake_additional_variables_prefixes", ["LIBDWARF"])
        deps.set_property("libevent", "cmake_additional_variables_prefixes", ["LIBEVENT"])
        deps.set_property("libiberty", "cmake_additional_variables_prefixes", ["LIBIBERTY"])
        deps.set_property("libsodium", "cmake_additional_variables_prefixes", ["LIBSODIUM"])
        deps.set_property("libunwind", "cmake_additional_variables_prefixes", ["LIBUNWIND"])
        deps.set_property("liburing", "cmake_additional_variables_prefixes", ["LIBURING"])
        deps.set_property("libaio", "cmake_additional_variables_prefixes", ["LIBAIO"])
        deps.set_property("lz4", "cmake_additional_variables_prefixes", ["LZ4"])
        deps.set_property("openssl", "cmake_additional_variables_prefixes", ["OPENSSL"])
        deps.set_property("snappy", "cmake_additional_variables_prefixes", ["SNAPPY"])
        deps.set_property("xz_utils", "cmake_additional_variables_prefixes", ["LIBLZMA"])
        deps.set_property("zlib", "cmake_additional_variables_prefixes", ["ZLIB"])
        deps.set_property("zstd", "cmake_additional_variables_prefixes", ["ZSTD"])
        deps.generate()

    def build(self):
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
        self.cpp_info.components["libfolly"].requires = (
                ["fmt::fmt"] +
                [f"boost::{comp}" for comp in self._required_boost_components] +
                ["gflags::gflags",
                 "glog::glog",
                 "libevent::libevent",
                 "lz4::lz4",
                 "openssl::openssl",
                 "bzip2::bzip2",
                 "snappy::snappy",
                 "zlib::zlib",
                 "zstd::zstd",
                 "libsodium::libsodium",
                 "xz_utils::xz_utils",
                 "fast_float::fast_float"]
        )
        if not is_msvc(self):
            self.cpp_info.components["libfolly"].requires.append("libdwarf::libdwarf")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libfolly"].requires.extend(["libiberty::libiberty", "libunwind::libunwind"])
        if self.settings.os == "Linux":
            self.cpp_info.components["libfolly"].requires.extend(["liburing::liburing", "libaio::libaio"])
            self.cpp_info.components["libfolly"].system_libs.extend(["pthread", "dl", "rt"])
            self.cpp_info.components["libfolly"].defines.extend(["FOLLY_HAVE_ELF", "FOLLY_HAVE_DWARF"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["libfolly"].system_libs.extend(["ws2_32", "iphlpapi", "crypt32"])

        if  self.settings.get_safe("compiler.libcxx") == "libstdc++" or \
            (self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version.value) == "9.0" and \
              self.settings.get_safe("compiler.libcxx") == "libc++"):
            self.cpp_info.components["libfolly"].system_libs.append("atomic")

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version.value) >= "11.0":
            self.cpp_info.components["libfolly"].system_libs.append("c++abi")

        self.cpp_info.components["follybenchmark"].set_property("cmake_target_name", "Folly::follybenchmark")
        self.cpp_info.components["follybenchmark"].set_property("pkg_config_name", "libfollybenchmark")
        self.cpp_info.components["follybenchmark"].libs = ["follybenchmark"]
        self.cpp_info.components["follybenchmark"].requires = ["libfolly"]

        self.cpp_info.components["folly_test_util"].set_property("cmake_target_name", "Folly::folly_test_util")
        self.cpp_info.components["folly_test_util"].set_property("pkg_config_name", "libfolly_test_util")
        self.cpp_info.components["folly_test_util"].libs = ["folly_test_util"]
        self.cpp_info.components["folly_test_util"].requires = ["libfolly"]

        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            # exception tracer (renamed + granular)
            cmp_exc = "folly_debugging_exception_tracer_"
            for lib in [
                "exception_tracer_base",
                "exception_tracer",
                "exception_tracer_callbacks",
                "exception_counter",
                "exception_counter_static_registration",
                "stacktrace",
                "smart_exception_tracer_singleton",
                "smart_exception_tracer",
                "smart_exception_stack_trace_hooks",
            ]:
                self.cpp_info.components[cmp_exc + lib].set_property("cmake_target_name", f"Folly::{cmp_exc}{lib}")
                self.cpp_info.components[cmp_exc + lib].libs = [cmp_exc + lib]
                self.cpp_info.components[cmp_exc + lib].requires = ["libfolly"]

            # symbolizer
            cmp_sym = "folly_debugging_symbolizer_"
            for lib in [
                "elf",
                "elf_cache",
                "line_reader",
                "symbolized_frame",
                "dwarf",
                "stack_trace",
                "detail_debug",
                "symbolizer",
            ]:
                self.cpp_info.components[cmp_sym + lib].set_property("cmake_target_name", f"Folly::{cmp_sym}{lib}")
                self.cpp_info.components[cmp_sym + lib].libs = [cmp_sym + lib]
                self.cpp_info.components[cmp_sym + lib].requires = ["libfolly"]
