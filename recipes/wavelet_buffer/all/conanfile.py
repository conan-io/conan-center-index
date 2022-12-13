from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.50"


class WaveletBufferConan(ConanFile):
    name = "wavelet_buffer"
    license = "MPL-2.0"
    description = "An universal C++ compression library based on wavelet transformation"
    topics = ("compression", "signal-processing", "wavelet")
    homepage = "https://github.com/panda-official/WaveletBuffer"
    url = "https://github.com/conan-io/conan-center-index"
    default_options = {
        "cimg/*:enable_fftw": False,
        "cimg/*:enable_jpeg": False,
        "cimg/*:enable_openexr": False,
        "cimg/*:enable_png": False,
        "cimg/*:enable_tiff": False,
        "cimg/*:enable_ffmpeg": False,
        "cimg/*:enable_opencv": False,
        "shared": False,
        "fPIC": True,
    }

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}

    def requirements(self):
        self.requires("openblas/0.3.20")
        self.requires("blaze/3.8")
        self.requires("libjpeg-turbo/2.1.2")
        self.requires("cimg/3.0.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True,
        )

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_EXPORTED"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "8",
            "clang": "12",
            "apple-clang": "12",
        }

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        # Compiler version check
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._minimum_compilers_version.get(
                str(self.info.settings.compiler), False
            )
            if not minimum_version:
                self.output.warn(
                    "{} recipe lacks information about the {} compiler support.".format(
                        self.name, self.settings.compiler
                    )
                )
            else:
                if Version(self.info.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(
                        "{} requires C++{} support. The current compiler {} {} does not support it.".format(
                            self.ref,
                            self._minimum_cpp_standard,
                            self.settings.compiler,
                            self.settings.compiler.version,
                        )
                    )

        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} can not be built as shared on Visual Studio and msvc."
            )

        # Dependency options check
        cimg = self.dependencies["cimg"]
        if cimg.options.enable_fftw:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_fftw=False'"
            )
        if cimg.options.enable_jpeg:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_jpeg=False'"
            )
        if cimg.options.enable_openexr:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_openexr=False'"
            )
        if cimg.options.enable_tiff:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_tiff=False'"
            )
        if cimg.options.enable_png:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_png=False'"
            )
        if cimg.options.enable_ffmpeg:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_ffmpeg=False'"
            )
        if cimg.options.enable_opencv:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires the option 'cimg:enable_opencv=False'"
            )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["wavelet_buffer", "sf_compressor"]
        self.cpp_info.set_property("cmake_file_name", "wavelet_buffer")
        self.cpp_info.set_property(
            "cmake_target_name", "wavelet_buffer::wavelet_buffer"
        )

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "wavelet_buffer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "wavelet_buffer"
        self.cpp_info.names["cmake_find_package"] = "wavelet_buffer"
        self.cpp_info.names["cmake_find_package_multi"] = "wavelet_buffer"
