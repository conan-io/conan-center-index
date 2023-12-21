from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, check_min_vs
import os

required_conan_version = ">=1.57.0"


class CubicInterpolationConan(ConanFile):
    name = "cubicinterpolation"
    description = "Leightweight interpolation library based on boost and eigen."
    license = "MIT"
    homepage = "https://github.com/MaxSac/cubic_interpolation"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("interpolation", "splines", "cubic", "bicubic", "boost", "eigen3")
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
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TODO: update boost dependency as soon as we deprecate conan1.x (see discussion in #11207)
        self.requires("boost/1.83.0")
        self.requires("eigen/3.4.0")

    @property
    def _required_boost_components(self):
        return ["filesystem", "math", "serialization"]

    def validate(self):
        miss_boost_required_comp = any(getattr(self.dependencies["boost"].options, f"without_{boost_comp}", True) for boost_comp in self._required_boost_components)
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires non header-only boost with these components: "
                f"{', '.join(self._required_boost_components)}",
            )

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "14")

        if not check_min_vs(self, 192, raise_invalid=False):
            raise ConanInvalidConfiguration(f"{self.ref} currently Visual Studio < 2019 not yet supported in this recipe. Contributions are welcome")

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared is not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLE"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CubicInterpolation")
        self.cpp_info.set_property("cmake_target_name", "CubicInterpolation::CubicInterpolation")
        self.cpp_info.libs = ["CubicInterpolation"]
        self.cpp_info.requires = ["boost::headers", "boost::filesystem", "boost::math", "boost::serialization", "eigen::eigen"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CubicInterpolation"
        self.cpp_info.names["cmake_find_package_multi"] = "CubicInterpolation"
