import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches
from conan.tools.files import get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class HexlConan(ConanFile):
    name = "hexl"
    description = "Intel Homomorphic Encryption (HE) Acceleration Library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/hexl"
    topics = ("homomorphic", "encryption", "privacy")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "experimental": [True, False],
        "fpga_compatibility_dyadic_multiply": [True, False],
        "fpga_compatibility_keyswitch": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "experimental": False,
        "fpga_compatibility_dyadic_multiply": False,
        "fpga_compatibility_keyswitch": False,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "11",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpu_features/0.8.0")

        if self.settings.build_type == "Debug":
            self.requires("easyloggingpp/9.97.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++17, which your compiler does not support."
                )
        else:
            self.output.warning(
                f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17."
            )

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Hexl only supports x86 architecture")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["HEXL_BENCHMARK"] = False
        tc.variables["HEXL_TESTING"] = False
        tc.variables["HEXL_EXPERIMENTAL"] = self.options.experimental

        if self.options.fpga_compatibility_dyadic_multiply and self.options.fpga_compatibility_keyswitch:
            tc.variables["HEXL_FPGA_COMPATIBILITY"] = 3
        elif self.options.fpga_compatibility_dyadic_multiply:
            tc.variables["HEXL_FPGA_COMPATIBILITY"] = 1
        elif self.options.fpga_compatibility_keyswitch:
            tc.variables["HEXL_FPGA_COMPATIBILITY"] = 2
        else:
            tc.variables["HEXL_FPGA_COMPATIBILITY"] = 0

        tc.variables["HEXL_SHARED_LIB"] = self.options.shared
        tc.variables["HEXL_CROSS_COMPILED"] = cross_building(self)

        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared

        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("easyloggingpp", "cmake_file_name", "EASYLOGGINGPP")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Hexl")
        # TODO: Remove in Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "Hexl"
        self.cpp_info.names["cmake_find_package_multi"] = "Hexl"

        if self.settings.build_type == "Debug":
            if not is_msvc(self):
                self.cpp_info.components["Hexl"].libs = ["hexl_debug"]
            else:
                self.cpp_info.components["Hexl"].libs = ["hexl"]

            self.cpp_info.components["Hexl"].requires.append("easyloggingpp::easyloggingpp")
        else:
            self.cpp_info.components["Hexl"].libs = ["hexl"]

        self.cpp_info.components["Hexl"].names["cmake_find_package"] = "hexl"
        self.cpp_info.components["Hexl"].names["cmake_find_package_multi"] = "hexl"
        self.cpp_info.components["Hexl"].set_property("cmake_target_name", "Hexl::hexl")
        self.cpp_info.components["Hexl"].set_property("pkg_config_name", "hexl")
        self.cpp_info.components["Hexl"].requires.append("cpu_features::libcpu_features")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["Hexl"].system_libs = ["pthread", "m"]
