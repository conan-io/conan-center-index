from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import get
from conan.tools.files import apply_conandata_patches, export_conandata_patches
from os import path

class NFIRConan(ConanFile):
    name = "nfir"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/usnistgov/NFIR"
    topics = ("NIST", "NFIR")
    license = "NIST-PD"
    description = "The NIST Fingerprint Image Resampler NFIR is a library capable of upsampling or downsampling fingerprint images."
    settings = "os", "compiler", "build_type", "arch"
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }
    generators = "CMakeDeps"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opencv/4.10.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_NFIMM"] = False
        tc.variables["_WIN32_64"] = self.settings.os == "Windows"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["NFIR_ITL"]
        self.cpp_info.set_property("cmake_file_name", "NFIR")
        self.cpp_info.set_property("cmake_target_name", "NFIR::NFIR")
        self.runenv_info.append_path("PATH", path.join(self.package_folder, "bin"))