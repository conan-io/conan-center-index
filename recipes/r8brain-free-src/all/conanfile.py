from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class R8brainFreeSrcConan(ConanFile):
    name = "r8brain-free-src"
    description = "High-quality pro audio sample rate converter / resampler C++ library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/avaneev/r8brain-free-src"
    topics = ("audio", "sample-rate", "conversion", "audio-processing", "resampler")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fft": ["ooura", "pffft", "pffft_double", ]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fft": "ooura",
    }
    exports_sources = ["CMakeLists.txt"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.fft == "pffft":
            self.requires("pffft/cci.20210511")
        # TODO: use pffft_double package when possible

    def validate(self):
        if self.options.fft == "ooura" and is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built shared with Visual Studio")

        if self.options.fft == "pffft_double" and Version(self.version) < "4.10":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support pffft_double")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["R8BRAIN_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["R8BRAIN_WITH_PFFFT"] = self.options.fft == "pffft"
        tc.variables["R8BRAIN_WITH_PFFFT_DOUBLE"] = self.options.fft == "pffft_double"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["r8brain"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m",])

        if self.options.fft == "pffft":
            self.cpp_info.defines.append("R8B_PFFFT")
        if self.options.fft == "pffft_double":
            self.cpp_info.defines.append("R8B_PFFFT_DOUBLE")
