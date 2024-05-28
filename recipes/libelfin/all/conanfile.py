from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibelfinConan(ConanFile):
    name = "libelfin"
    description = "C++11 library for reading ELF binaries and DWARFv4 debug information"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aclements/libelfin"
    topics = ("elf", "dwarf")

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
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"libelfin doesn't support compiler: {self.settings.compiler}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["libelfin_VERSION"] = self.version
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.export_sources_folder, dst=self.source_folder)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libelf++"].set_property("pkg_config_name", "libelf++")
        self.cpp_info.components["libelf++"].libs = ["elf++"]
        self.cpp_info.components["libdwarf++"].set_property("pkg_config_name", "libdwarf++")
        self.cpp_info.components["libdwarf++"].libs = ["dwarf++"]
        self.cpp_info.components["libdwarf++"].requires = ["libelf++"]

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.components["libelf++"].names["pkg_config"] = "libelf++"
        self.cpp_info.components["libdwarf++"].names["pkg_config"] = "libdwarf++"
