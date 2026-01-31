from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"

class PackageConan(ConanFile):
    name = "or-tools"
    description = "Google OR Tools"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developers.google.com/optimization"
    topics = ("optimization", "linear-programming", "operations-research", "combinatorial-optimization", "or-tools")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20250814.0", transitive_headers=True) # source is 20250814.1 which conflicts with protobuf 32.1 at 20250814.0
        self.requires("bzip2/1.0.8")
        self.requires("coin-clp/[>=1.17.7 <=1.17.10]") # source is 1.17.10
        self.requires("coin-osi/[>=0.108.7 <=0.108.11]") # source is 0.108.11
        self.requires("coin-utils/[>=2.11.9 <3]") # coin-clp 1.17.7 requires an older version for now
        self.requires("coin-cbc/[>=2.10.5 <=2.10.12]") # source is 2.10.12
        self.requires("eigen/3.4.0")
        self.requires("highs/1.12.0")
        self.requires("protobuf/6.32.1", transitive_headers=True) # source is 33.1
        self.requires("re2/[>=20250812]") # source is 20250812, but only 20250722 or 20251105 are in conan center
        self.requires("scip/10.0.0")
        self.requires("zlib/1.3.1")

    def validate(self):
        if is_msvc(self):
            check_min_cppstd(self, 20)
        else:
            check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan manage the C++ standard based on self.settings.compiler.cppstd
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD", "#set(CMAKE_CXX_STANDARD")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "dependencies", "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD", "#set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["BUILD_Boost"] = False
        tc.cache_variables["BUILD_SCIP"] = False
        tc.cache_variables["BUILD_soplex"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_SAMPLES"] = False
        tc.cache_variables["BUILD_CXX_EXAMPLES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("scip", "cmake_file_name", "SCIP")
        deps.set_property("scip", "cmake_target_name", "SCIP::libscip")
        deps.set_property("coin-utils", "cmake_file_name", "CoinUtils")
        deps.set_property("coin-utils", "cmake_target_name", "Coin::CoinUtils")
        deps.set_property("coin-cgl", "cmake_file_name", "Cgl")
        deps.set_property("coin-cgl", "cmake_target_name", "Coin::Cgl")
        deps.set_property("coin-cbc", "cmake_file_name", "Cbc")
        deps.set_property("coin-cbc", "cmake_target_name", "Coin::Cbc")
        deps.set_property("coin-cbc::libcbc", "cmake_target_name", "Coin::CbcSolver")
        deps.set_property("coin-cbc::osi-cbc", "cmake_target_name", "Coin::OsiCbc")
        deps.set_property("coin-clp", "cmake_file_name", "Clp")
        deps.set_property("coin-clp", "cmake_target_name", "Coin::Clp")
        deps.set_property("coin-clp::clp", "cmake_target_name", "Coin::ClpSolver")
        deps.set_property("coin-clp::osi-clp", "cmake_target_name", "Coin::OsiClp")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["ortools"]
        self.cpp_info.set_property("cmake_file_name", "ortools")
        self.cpp_info.components["ortools"].libs = ["ortools"]

        # INFO: In order to use ortools::solve, it requires the experimental Conan generator CMakeConfigDeps
        self.cpp_info.components["solve"].exe = ["solve"]
        self.cpp_info.components["solve"].set_property("cmake_target_name", "ortools::solve")
        # INFO: In order to use ortools::fzn, it requires the experimental Conan generator CMakeConfigDeps
        self.cpp_info.components["fzn"].exe = ["fzn-cp-sat"]
        self.cpp_info.components["fzn"].set_property("cmake_target_name", "ortools::fzn")

        self.cpp_info.components["ortools"].set_property("cmake_target_name", "ortools::ortools")
        self.cpp_info.components["ortools"].defines = ["OR_PROTO_DLL=;USE_MATH_OPT;USE_BOP;USE_CBC;USE_GLOP;USE_HIGHS;USE_PDLP;USE_SCIP"]
        self.cpp_info.components["ortools"].requires = [
            "zlib::zlib",
            "bzip2::bzip2",
            "abseil::absl_base",
            "abseil::absl_core_headers",
            "abseil::absl_absl_check",
            "abseil::absl_absl_log",
            "abseil::absl_check",
            "abseil::absl_die_if_null",
            "abseil::absl_flags",
            "abseil::absl_flags_commandlineflag",
            "abseil::absl_flags_marshalling",
            "abseil::absl_flags_parse",
            "abseil::absl_flags_reflection",
            "abseil::absl_flags_usage",
            "abseil::absl_log",
            "abseil::absl_log_flags",
            "abseil::absl_log_globals",
            "abseil::absl_log_initialize",
            "abseil::absl_log_internal_message",
            "abseil::absl_cord",
            "abseil::absl_random_random",
            "abseil::absl_raw_hash_set",
            "abseil::absl_hash",
            "abseil::absl_leak_check",
            "abseil::absl_memory",
            "abseil::absl_meta",
            "abseil::absl_stacktrace",
            "abseil::absl_status",
            "abseil::absl_statusor",
            "abseil::absl_str_format",
            "abseil::absl_strings",
            "abseil::absl_synchronization",
            "abseil::absl_time",
            "abseil::absl_any",
            "protobuf::libprotobuf",
            "re2::re2",
            "coin-cbc::libcbc",
            "coin-cbc::osi-cbc",
            "coin-clp::clp",
            "coin-clp::osi-clp",
            "coin-osi::libosi",
            "coin-utils::coin-utils",
            "highs::highs",
            "eigen::eigen3",
            "scip::scip"
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ortools"].system_libs.extend(["m", "pthread", "dl"])

        self.cpp_info.components["flatzinc"].libs = ["ortools_flatzinc"]
        self.cpp_info.components["flatzinc"].set_property("cmake_target_name", "ortools::flatzinc")
        self.cpp_info.components["flatzinc"].requires = ["ortools"]
