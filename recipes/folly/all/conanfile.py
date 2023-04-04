from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
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
        return "17" if Version(self.version) >= "2022.01.31.00" else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "6",
            "apple-clang": "8",
        } if self._min_cppstd == "14" else {
            "gcc": "7",
            "Visual Studio": "16",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if str(self.settings.arch) not in ['x86', 'x86_64']:
            del self.options.use_sse4_2

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.78.0", transitive_headers=True)
        self.requires("bzip2/1.0.8")
        self.requires("double-conversion/3.2.0", transitive_headers=True)
        self.requires("gflags/2.2.2", transitive_headers=True)
        self.requires("glog/0.4.0", transitive_headers=True)
        self.requires("libevent/2.1.12", transitive_headers=True)
        self.requires("openssl/1.1.1t", transitive_headers=True)
        self.requires("lz4/1.9.3")
        self.requires("snappy/1.1.9")
        self.requires("zlib/1.2.13", transitive_headers=True)
        self.requires("zstd/1.5.2", transitive_headers=True)
        if not is_msvc(self):
            self.requires("libdwarf/20191104")
        self.requires("libsodium/1.0.18")
        self.requires("xz_utils/5.4.0")
        # FIXME: Causing compilation issues on clang: self.requires("jemalloc/5.2.1")
        if self.settings.os == "Linux":
            self.requires("libiberty/9.1.0")
            self.requires("libunwind/1.6.2", transitive_headers=True)
        if "2020.08.10.00" <= Version(self.version) < "2022.01.31.00":
            self.requires("fmt/7.1.3", transitive_headers=True)
        if Version(self.version) >= "2022.01.31.00":
            self.requires("fmt/8.0.1", transitive_headers=True)  # Folly bump fmt to 8.0.1 in v2022.01.31.00

    @property
    def _required_boost_components(self):
        return ["context", "filesystem", "program_options", "regex", "system", "thread"]

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if Version(self.version) < "2022.01.31.00" and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Conan support for non-Linux platforms starts with Folly version 2022.01.31.00")

        if self.settings.os == "Macos" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Conan currently requires a 64bit target architecture for Folly on Macos")

        if self.settings.os == "Windows" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture on Windows")

        if self.settings.os in ["Macos", "Windows"] and self.options.shared:
            raise ConanInvalidConfiguration(f"Folly could not be built on {self.settings.os} as shared library")

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} could not be built on {self.settings.os}. PR's are welcome.")
        
        if Version(self.version) >= "2020.08.10.00" and self.settings.compiler == "clang" and self.options.shared:
            raise ConanInvalidConfiguration(f"Folly {self.version} could not be built by clang as a shared library")

        boost = self.dependencies["boost"]
        if boost.options.header_only:
            raise ConanInvalidConfiguration("Folly could not be built with a header only Boost")

        miss_boost_required_comp = any(getattr(boost.options, f"without_{boost_comp}", True) for boost_comp in self._required_boost_components)
        if miss_boost_required_comp:
            required_components = ", ".join(self._required_boost_components)
            raise ConanInvalidConfiguration(f"Folly requires these boost components: {required_components}")

        if self.options.get_safe("use_sse4_2") and str(self.settings.arch) not in ['x86', 'x86_64']:
            raise ConanInvalidConfiguration(f"{self.ref} can use the option use_sse4_2 only on x86 and x86_64 archs.")

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output=output)
            m = re.search(r'cmake version (\d+\.\d+\.\d+)', output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if not self._cmake_new_enough("3.13"):  # Make sure CMP0077 is honored
            self.tool_requires("cmake/3.25.3")

    def _preserve_tarball_root(self):
        return Version(self.version) >= "2022.01.31.00"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=not self._preserve_tarball_root())

    def _cppstd_flag_value(self, cppstd):
        cppstd_prefix_gnu, cppstd_value = (cppstd[:3], cppstd[3:]) if "gnu" in cppstd else ("", cppstd)
        if not cppstd_prefix_gnu:
            cppstd_prefix_gnu = "c"
        if is_msvc(self):
            cppstd_prefix_gnu = ""
            if cppstd_value > "17":
                cppstd_value = "latest"
        cxx_std_value = f"{cppstd_prefix_gnu}++{cppstd_value}"
        return cxx_std_value

    def generate(self):
        tc = CMakeToolchain(self)
        if can_run(self):
            tc.variables["FOLLY_HAVE_UNALIGNED_ACCESS_EXITCODE"] = "0"
            tc.variables["FOLLY_HAVE_UNALIGNED_ACCESS_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.variables["FOLLY_HAVE_LINUX_VDSO_EXITCODE"] = "0"
            tc.variables["FOLLY_HAVE_LINUX_VDSO_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.variables["FOLLY_HAVE_WCHAR_SUPPORT_EXITCODE"] = "0"
            tc.variables["FOLLY_HAVE_WCHAR_SUPPORT_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.variables["HAVE_VSNPRINTF_ERRORS_EXITCODE"] = "0"
            tc.variables["HAVE_VSNPRINTF_ERRORS_EXITCODE__TRYRUN_OUTPUT"] = ""

        if self.options.get_safe("use_sse4_2") and str(self.settings.arch) in ['x86', 'x86_64']:
            tc.preprocessor_definitions["FOLLY_SSE"] = "4"
            tc.preprocessor_definitions["FOLLY_SSE_MINOR"] = "2"
            if not is_msvc(self):
                tc.variables["CMAKE_C_FLAGS"] = "-mfma"
                tc.variables["CMAKE_CXX_FLAGS"] = "-mfma"
            else:
                tc.variables["CMAKE_C_FLAGS"] = "/arch:FMA"
                tc.variables["CMAKE_CXX_FLAGS"] = "/arch:FMA"

        # Folly is not respecting this from the helper https://github.com/conan-io/conan-center-index/pull/15726/files#r1097068754
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor CMAKE_REQUIRED_LIBRARIES in check_include_file_xxx
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0075"] = "NEW"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        cxx_std_value = self._cppstd_flag_value(self.settings.get_safe("compiler.cppstd", self._min_cppstd))
        # 2019.10.21.00 -> either MSVC_ flags or CXX_STD
        if is_msvc(self):
            tc.variables["MSVC_LANGUAGE_VERSION"] = cxx_std_value
            tc.variables["MSVC_ENABLE_ALL_WARNINGS"] = False
            tc.variables["MSVC_USE_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
        else:
            tc.variables["CXX_STD"] = cxx_std_value

        if not self.dependencies["boost"].options.header_only:
            tc.cache_variables["BOOST_LINK_STATIC"] = not self.dependencies["boost"].options.shared

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0074"] = "NEW"  # Honor Boost_ROOT set by boost recipe
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        folly_deps = os.path.join(self.source_folder, "CMake", "folly-deps.cmake")
        replace_in_file(self, folly_deps, "MODULE", "")

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
        self.cpp_info.set_property("cmake_target_name", "Folly::folly")
        self.cpp_info.set_property("pkg_config_name", "libfolly")

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
            "boost::context", "boost::filesystem", "boost::program_options", "boost::regex", "boost::system", "boost::thread",
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

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["libfolly"].system_libs.append("stdc++fs")

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["libfolly"].system_libs.append("stdc++fs" if self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] else "c++fs")

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

        if Version(self.version) >= "2019.10.21.00":
            # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
            self.cpp_info.components["follybenchmark"].names["cmake_find_package"] = "follybenchmark"
            self.cpp_info.components["follybenchmark"].names["cmake_find_package_multi"] = "follybenchmark"
            self.cpp_info.components["folly_test_util"].names["cmake_find_package"] = "folly_test_util"
            self.cpp_info.components["folly_test_util"].names["cmake_find_package_multi"] = "folly_test_util"

            self.cpp_info.components["follybenchmark"].set_property("cmake_target_name", "Folly::follybenchmark")
            self.cpp_info.components["follybenchmark"].set_property("pkg_config_name", "libfollybenchmark")
            self.cpp_info.components["follybenchmark"].libs = ["follybenchmark"]
            self.cpp_info.components["follybenchmark"].requires = ["libfolly"]

            self.cpp_info.components["folly_test_util"].set_property("cmake_target_name", "Folly::folly_test_util")
            self.cpp_info.components["folly_test_util"].set_property("pkg_config_name", "libfolly_test_util")
            self.cpp_info.components["folly_test_util"].libs = ["folly_test_util"]
            self.cpp_info.components["folly_test_util"].requires = ["libfolly"]

        if Version(self.version) >= "2020.08.10.00" and self.settings.os == "Linux":
            # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
            self.cpp_info.components["folly_exception_tracer_base"].names["cmake_find_package"] = "folly_exception_tracer_base"
            self.cpp_info.components["folly_exception_tracer_base"].names["cmake_find_package_multi"] = "folly_exception_tracer_base"
            self.cpp_info.components["folly_exception_tracer"].names["cmake_find_package"] = "folly_exception_tracer"
            self.cpp_info.components["folly_exception_tracer"].names["cmake_find_package_multi"] = "folly_exception_tracer"
            self.cpp_info.components["folly_exception_counter"].names["cmake_find_package"] = "folly_exception_counter"
            self.cpp_info.components["folly_exception_counter"].names["cmake_find_package_multi"] = "folly_exception_counter"

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


    #  Folly release every two weeks and it is hard to maintain cmake scripts.
    #  This script is used to fix CMake/folly-deps.cmake.
    #  I attach it here for convenience. All the 00xx-find-packages.patches are generated by this script
    #     ```shell
    #     sed -i 's/^find_package(Boost.*$/find_package(Boost  /' CMake/folly-deps.cmake
    #     sed -i 's/DoubleConversion MODULE/double-conversion /ig' CMake/folly-deps.cmake
    #     sed -i 's/DOUBLE_CONVERSION/double-conversion/ig' CMake/folly-deps.cmake
    #     sed -i 's/^find_package(Gflags.*$/find_package(gflags  REQUIRED)/g' CMake/folly-deps.cmake
    #     sed -i 's/LIBGFLAGS_FOUND/gflags_FOUND/g'  CMake/folly-deps.cmake
    #     sed -i 's/[^_]LIBGFLAGS_LIBRARY/{gflags_LIBRARIES/'  CMake/folly-deps.cmake
    #     sed -i 's/[^_]LIBGFLAGS_INCLUDE/{gflags_INCLUDE/'  CMake/folly-deps.cmake
    #     sed -i 's/find_package(Glog MODULE)/find_package(glog  REQUIRED)/g' CMake/folly-deps.cmake
    #     sed -i 's/GLOG_/glog_/g' CMake/folly-deps.cmake
    #     sed -i 's/find_package(LibEvent MODULE/find_package(Libevent /' CMake/folly-deps.cmake
    #     sed -i 's/LIBEVENT_/Libevent_/ig' CMake/folly-deps.cmake
    #     sed -i 's/OPENSSL_LIB/OpenSSL_LIB/g' CMake/folly-deps.cmake
    #     sed -i 's/OPENSSL_INCLUDE/OpenSSL_INCLUDE/g' CMake/folly-deps.cmake
    #     sed -i 's/BZIP2_/BZip2_/g' CMake/folly-deps.cmake
    #     sed -i 's/(LZ4/(lz4/g' CMake/folly-deps.cmake
    #     sed -i 's/LZ4_/lz4_/g' CMake/folly-deps.cmake
    #     sed -i 's/Zstd /zstd /g'  CMake/folly-deps.cmake
    #     sed -i 's/ZSTD_/zstd_/g' CMake/folly-deps.cmake
    #     sed -i 's/(LibDwarf/(libdwarf/g' CMake/folly-deps.cmake
    #     sed -i 's/LIBDWARF_/libdwarf_/g' CMake/folly-deps.cmake
    #     sed -i 's/Libiberty/libiberty/g' CMake/folly-deps.cmake
    #     sed -i 's/Libsodium/libsodium/ig' CMake/folly-deps.cmake
    #     sed -i 's/LibUnwind/libunwind/g' CMake/folly-deps.cmake
    #     sed -i 's/LibUnwind_/libunwind_/ig' CMake/folly-deps.cmake
    #     ```
