from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
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
        "with_glpk": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "with_glpk": False,
        "shared": True,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20250814.0", transitive_headers=True, transitive_libs=True) # source is 20250814.1 which conflicts with protobuf 32.1 at 20250814.0
        #self.requires("boost/1.87.0") # build this because conan version lacks Boost::multiprecision or Boost::serialization
        self.requires("bzip2/1.0.8")
        self.requires("coin-clp/[>=1.17.7 <=1.17.10]") # source is 1.17.10
        self.requires("coin-osi/[>=0.108.7 <=0.108.11]") # source is 0.108.11
        self.requires("coin-utils/2.11.12", override=True) # coin-clp 1.17.7 requires an older version for now
        self.requires("coin-cbc/[>=2.10.5 <=2.10.12]") # source is 2.10.12
        self.requires("eigen/3.4.0")
        self.requires("highs/1.12.0")
        self.requires("protobuf/6.32.1", transitive_headers=True) # source is 33.1
        self.requires("re2/[>=20250812]") # source is 20250812, but only 20250722 or 20251105 are in conan center
        #self.requires("scip/10.0.0") # build this due to not having SCIP::libscip target
        #self.requires("soplex/[>=7.1.3]") # build this due to conflicts in lib name for targets
        self.requires("zlib/1.3.1")

    def validate(self):
        if is_msvc(self):
            check_min_cppstd(self, 20)
        else:
            check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        self.tool_requires("protobuf/6.32.1") # source is 33.1

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["BUILD_Boost"] = True
        tc.cache_variables["BUILD_SCIP"] = True
        tc.cache_variables["BUILD_soplex"] = True
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_SAMPLES"] = False
        tc.cache_variables["BUILD_CXX_EXAMPLES"] = False
        tc.generate()

        deps = CMakeDeps(self)
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

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["ortools"]
        self.cpp_info.set_property("cmake_module_file_name", "ortools")
        self.cpp_info.set_property("cmake_module_target_name", "ortools::ortools")
        self.cpp_info.set_property("cmake_file_name", "ortools")
        self.cpp_info.set_property("cmake_target_name", "ortools::ortools")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
