import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, save, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class OrToolsConan(ConanFile):
    name = "or-tools"
    description = "OR-Tools is fast and portable software for combinatorial optimization"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developers.google.com/optimization/"
    topics = ("optimization", "linear-programming", "operations-research", "combinatorial-optimization")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_lp_parser": [True, False],
        "with_coinor": [True, False],
        "with_glpk": [True, False],
        "with_highs": [True, False],
        "with_scip": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lp_parser": False,  # FIXME: has an abseil version conflict with protobuf
        "with_coinor": True,
        "with_glpk": True,
        "with_highs": True,
        "with_scip": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("protobuf/5.27.0")
        self.requires("abseil/20240116.2")
        self.requires("eigen/3.4.0")
        if self.options.build_lp_parser:
            self.requires("re2/20240702")
        if self.options.with_coinor:
            self.requires("coin-utils/2.11.11")
            self.requires("coin-osi/0.108.10")
            self.requires("coin-clp/1.17.9")
            self.requires("coin-cgl/0.60.8")
            self.requires("coin-cbc/2.10.11")
        if self.options.with_glpk:
            self.requires("glpk/4.48")
        if self.options.with_highs:
            self.requires("highs/1.8.1")
        if self.options.with_scip:
            self.requires("scip/9.2.0")

    def validate(self):
        if is_msvc(self):
            check_min_cppstd(self, 20)
        else:
            check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")
        self.tool_requires("protobuf/<host_version>")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # protoc is available from Conan when cross-compiling, no need to fetch and build it
        save(self, os.path.join(self.source_folder, "cmake", "host.cmake"), "")
        # Let Conan set the C++ standard
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD", "# set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DEPS"] = False
        tc.cache_variables["BUILD_SAMPLES"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_LP_PARSER"] = self.options.build_lp_parser
        tc.cache_variables["USE_COINOR"] = self.options.with_coinor
        tc.cache_variables["USE_GLPK"] = self.options.with_glpk
        tc.cache_variables["USE_HIGHS"] = self.options.with_highs
        tc.cache_variables["USE_SCIP"] = self.options.with_scip
        tc.cache_variables["USE_CPLEX"] = False  # TODO
        tc.cache_variables["BUILD_GLPK"] = False
        protoc_path = os.path.join(self.dependencies.build["protobuf"].cpp_info.bindir, "protoc")
        tc.cache_variables["PROTOC_PRG"] = protoc_path.replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("glpk", "cmake_file_name", "GLPK")
        deps.set_property("glpk", "cmake_target_name", "GLPK::GLPK")
        deps.set_property("scip", "cmake_file_name", "SCIP")
        deps.set_property("scip", "cmake_target_name", "libscip")
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ortools")
        self.cpp_info.set_property("cmake_target_name", "ortools::ortools")

        self.cpp_info.libs = ["ortools", "ortools_flatzinc"]
        self.cpp_info.resdirs = ["share"]

        self.cpp_info.defines.extend([
            "USE_MATH_OPT"
            "USE_BOP",
            "USE_GLOP",
            "USE_PDLP",
        ])
        if self.options.shared:
            self.cpp_info.defines.append("OR_TOOLS_AS_DYNAMIC_LIB")
        if self.options.build_lp_parser:
            self.cpp_info.defines.append("USE_LP_PARSER")
        if self.options.with_coinor:
            self.cpp_info.defines.extend(["USE_CBC", "USE_CLP"])
        if self.options.with_glpk:
            self.cpp_info.defines.append("USE_GLPK")
        if self.options.with_highs:
            self.cpp_info.defines.append("USE_HIGHS")
        if self.options.with_scip:
            self.cpp_info.defines.append("USE_SCIP")
        # self.cpp_info.defines.append("USE_CPLEX")
        # self.cpp_info.defines.append("USE_GUROBI")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
