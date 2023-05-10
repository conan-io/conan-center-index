from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get
from conan.tools.build import check_min_cppstd


required_conan_version = ">=1.59.0"


class fastgltf(ConanFile):
    name = "fastgltf"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/spnda/fastgltf"
    description = "A blazing fast C++17 glTF 2.0 library powered by SIMD."
    topics = ("gltf", "simd", "cpp17")

    # Needed for CMake configurations for dependencies to work
    generators = "CMakeDeps"

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_small_vector": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_small_vector": False,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder='src')

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, "17")

    def requirements(self):
        self.requires("simdjson/3.1.7")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FASTGLTF_DOWNLOAD_SIMDJSON"] = False
        if self.options.enable_small_vector:
            tc.variables["FASTGLTF_USE_SMALL_VECTOR"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fastgltf"]
