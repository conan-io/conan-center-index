from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get

required_conan_version = ">=1.50"


class WaveletBufferConan(ConanFile):
    name = "wavelet_buffer"
    license = "MPL-2.0"
    description = "An universal C++ compression library based on wavelet transformation"
    topics = ("compression", "signal-processing", "wavelet")
    homepage = "https://github.com/panda-official/WaveletBuffer"
    url = "https://github.com/conan-io/conan-center-index/recipes/wavelet_buffer"
    requires = "openblas/0.3.20", "blaze/3.8", "libjpeg-turbo/2.1.2", "cimg/3.0.2"
    default_options = {
        "cimg:enable_fftw": False,
        "cimg:enable_jpeg": False,
        "cimg:enable_openexr": False,
        "cimg:enable_png": False,
        "cimg:enable_tiff": False,
        "cimg:enable_ffmpeg": False,
        "cimg:enable_opencv": False,
        "shared": False,
        "fPIC": True,
    }

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}

    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        self.settings.build_type = "Release"

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_EXPORTED"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["wavelet_buffer", "sf_compressor"]
