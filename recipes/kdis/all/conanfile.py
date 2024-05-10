from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get

class kdisRecipe(ConanFile):
    name = "kdis"
    package_type = "library"

    # Optional metadata
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A complete open source implementation of DIS (Distributed Interactive Simulation)"
    topics = ("networking","simulation","protocols","dis","data-formats")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dis_version": ["5", "6", "7"],
        "use_enum_descriptors": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dis_version": "7",
        "use_enum_descriptors": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder,
            strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_EXAMPLES_TO_LINK_TO_LIB"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["USE_SOLUTION_FOLDERS"] = False
        tc.cache_variables["DIS_VERSION"] = self.options.dis_version
        tc.cache_variables["KDIS_USE_ENUM_DESCRIPTORS"] = self.options.use_enum_descriptors
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "KDIS::KDIS")
        self.cpp_info.defines = ["DIS_VERSION=" + str(self.options.dis_version)]
        self.cpp_info.libs = ["kdis"]
