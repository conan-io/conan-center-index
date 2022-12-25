from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, load, save
import os

required_conan_version = ">=1.45.0"


class PffftConan(ConanFile):
    name = "pffft"
    description = "PFFFT, a pretty fast Fourier Transform."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/jpommier/pffft/src/master/"
    topics = ("fft", "pffft")
    license = "BSD-like (FFTPACK license)"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_simd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_simd": False,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PFFFT_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["DISABLE_SIMD"] = self.options.disable_simd
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        header = load(self, os.path.join(self.source_folder, "pffft.h"))
        license_content = header[: header.find("*/", 1)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pffft"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
