from conan import ConanFile
from conan.tools.microsoft import check_min_vs
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class Z3Conan(ConanFile):
    name = "z3"
    description = "The Z3 Theorem Prover"
    topics = ("z3", "theorem", "smt", "satisfiability", "prover", "solver")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Z3Prover/z3"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithreaded": [True, False],
        "use_gmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
        "use_gmp": False
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "gcc": "7",
                "clang": "5",
                "apple-clang": "9.1",
            },
        }.get(self._min_cppstd, {})

    def patch_cmake_lists(self):
        # This function patches CMakeLists.txt to use the GMP library provided by Conan Center
        path = os.path.join(self.source_folder, "CMakeLists.txt")
        with open(path, "r") as file:
            content = file.read()
        content.replace("list(APPEND Z3_DEPENDENT_LIBS GMP::GMP)",
                        "list(APPEND Z3_DEPENDENT_LIBS gmp::gmp)",
                        1)
        with open(path, "w") as file:
            file.write(content)

    def export_sources(self):
        # Patch CMakeLists.txt for all supported Z3 versions
        # to use the GMP library provided by Conan Center
        # if and only if a user specifies to use GMP
        if self.options.use_gmp:
            self.patch_cmake_lists()
            self.output.info("CMakeLists.txt has been patched to use GMP provided by Conan Center.")
        # Then apply the patch designed for a specific range of Z3 versions
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
        if self.options.use_gmp:
            self.requires("gmp/6.2.1")

    def validate(self):
        # Z3 requires C++17, and it is recommended to use VS2019 or later
        check_min_vs(self, "192")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["Z3_USE_LIB_GMP"] = self.options.use_gmp
        tc.variables["Z3_SINGLE_THREADED"] = not self.options.multithreaded
        tc.variables["Z3_BUILD_LIBZ3_SHARED"] = self.options.shared
        tc.variables["Z3_INCLUDE_GIT_HASH"] = False
        tc.variables["Z3_INCLUDE_GIT_DESCRIBE"] = False
        tc.variables["Z3_ENABLE_EXAMPLE_TARGETS"] = False
        tc.variables["Z3_BUILD_DOCUMENTATION"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Z3")
        self.cpp_info.set_property("cmake_target_name", "z3::libz3")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libz3"].libs = [
            "libz3" if self.settings.os == "Windows" else "z3"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libz3"]\
                    .system_libs.extend(["pthread", "m"])
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Z3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Z3"
        self.cpp_info.names["cmake_find_package"] = "z3"
        self.cpp_info.names["cmake_find_package_multi"] = "z3"
        self.cpp_info.components["libz3"].names["cmake_find_package"] = "libz3"
        self.cpp_info.components["libz3"].names["cmake_find_package_multi"] = "libz3"
        self.cpp_info.components["libz3"].set_property("cmake_target_name", "z3::libz3")
        self.cpp_info.components["libz3"].requires = ["gmp::gmp"] if self.options.use_gmp else []
