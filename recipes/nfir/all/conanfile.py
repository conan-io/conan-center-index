from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import copy, get, collect_libs
from conan.tools.files import apply_conandata_patches
from os import path

class NFIRConan(ConanFile):
    name = "nfir"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/usnistgov/NFIR"
    topics = ("NIST, NFIR")
    license = "NIST"
    description = "The NIST Fingerprint Image Resampler NFIR is a library capable of upsampling or downsampling fingerprint images."
    settings = "os", "compiler", "build_type", "arch"
    options = { "shared": [True, False] }
    default_options = { "shared": False }
    generators = "CMakeDeps"
    package_type = "library"
    exports_sources = "CMakeLists.txt", "patches/*"

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("opencv/4.10.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["USE_NFIMM"] = False
        tc.variables["_WIN32_64"] = self.settings.os == "Windows"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*.h", src=path.join(self.source_folder, "src", "include"),  dst=path.join(self.package_folder, "include", "NFIR"), keep_path=False)
        copy(self, "*.lib", src=self.build_folder, dst=path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "NFIR*", src=path.join(self.build_folder, "bin"), dst=path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "libNFIR*", src=path.join(self.build_folder, "lib"), dst=path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["NFIR_ITL"]
        self.cpp_info.set_property("cmake_file_name", "NFIR")
        self.cpp_info.set_property("cmake_target_name", f"NFIR::NFIR")
        bindir = path.join(self.package_folder, "bin")
        self.runenv_info.append_path("PATH", bindir)
        self.buildenv_info.append_path("PATH", bindir)
        self.env_info.PATH.append(bindir)