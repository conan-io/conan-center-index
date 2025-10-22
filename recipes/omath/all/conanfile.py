from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class OmathConan(ConanFile):
    name = "omath"
    description = "Cross-platform modern general purpose math library written in C++23"
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/orange-cpp/omath"
    topics = ("math", "linear-algebra", "vector", "matrix")

    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "avx2": [True, False],
        "imgui": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "avx2": False,
        "imgui": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 23

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "13",
            "clang": "16",
            "apple-clang": "15",
            "Visual Studio": "17",
            "msvc": "193",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.avx2

    def configure(self):
        if is_msvc(self):
            del self.options.shared
            self.package_type = "static-library"
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.imgui:
            self.requires("imgui/1.91.8")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OMATH_USE_AVX2"] = self.options.get_safe("avx2", False)
        tc.variables["OMATH_IMGUI_INTEGRATION"] = self.options.imgui
        tc.variables["OMATH_USE_UNITY_BUILD"] = True
        tc.variables["OMATH_BUILD_TESTS"] = False
        tc.variables["OMATH_THREAT_WARNING_AS_ERROR"] = False
        tc.variables["OMATH_BUILD_BENCHMARK"] = False
        tc.variables["OMATH_BUILD_EXAMPLES"] = False
        tc.variables["OMATH_BUILD_AS_SHARED_LIBRARY"] = self.options.shared
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=f"{self.package_folder}/licenses")
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "omath")
        self.cpp_info.set_property("cmake_target_name", "omath::omath")
        
        self.cpp_info.libs = ["omath"]
        
        if self.options.imgui:
            self.cpp_info.requires = ["imgui::imgui"]
