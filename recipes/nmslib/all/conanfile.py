import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
from conan.tools.microsoft import is_msvc, check_min_vs

required_conan_version = ">=1.53.0"


class Nmslib(ConanFile):
    name = "nmslib"
    description = (
        "Non-Metric Space Library (NMSLIB): An efficient similarity search library "
        "and a toolkit for evaluation of k-NN methods for generic non-metric spaces."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nmslib/nmslib"
    topics = ("knn-search", "non-metric", "neighborhood-graphs", "neighborhood-graphs", "vp-tree")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_extras": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_extras": True,
    }
    options_description = {
        "build_extras": "Add support for Signature Quadratic Form Distance (SQFD). Not supported on MSVC.",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            # Not available on MSVC
            # https://github.com/nmslib/nmslib/blob/v2.1.1/similarity_search/include/space/space_sqfd.h#L19
            del self.options.build_extras

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("build_extras"):
            # Eigen is only used internally, no need for transitive_*
            self.requires("eigen/3.4.0")

    def validate(self):
        check_min_vs(self, 190)  # TODO: add reason in message
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Visual Studio shared builds are not supported (.lib artifacts missing)"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_EXTRAS"] = self.options.get_safe("build_extras", False)
        tc.variables["WITHOUT_TESTS"] = True
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "similarity_search", "CMakeLists.txt"),
                        "EIGEN3", "Eigen3")
        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        replace_in_file(self, os.path.join(self.source_folder, "similarity_search", "CMakeLists.txt"),
                        "-Ofast", "-Ofast -fno-finite-math-only")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "similarity_search"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["NonMetricSpaceLib"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
            if self.settings.arch in ["x86", "x86_64"]:
                self.cpp_info.system_libs.append("mvec")
        if self.options.get_safe("build_extras"):
            self.cpp_info.defines.append("WITH_EXTRAS")
