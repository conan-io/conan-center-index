from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class WaveletBufferConan(ConanFile):
    name = "wavelet_buffer"
    license = "MPL-2.0"
    description = "An universal C++ compression library based on wavelet transformation"
    topics = ("compression", "signal-processing", "wavelet")
    homepage = "https://github.com/panda-official/WaveletBuffer"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "jpeg": ["libjpeg-turbo", "libjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "jpeg": "libjpeg-turbo",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("blaze/3.8", transitive_headers=True)
        self.requires("cimg/[~3.3.2]") # version range covers up to last patch of 3.3.x
        if self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.1 <4]")
        else:
            self.requires("libjpeg/[>=9f]")
        # FIXME: unvendor SfCompressor which is currently downloaded at build time :s
        self.requires("streamvbyte/1.0.0")
        self.requires("fpzip/1.3.0")

    def validate(self):
        check_min_cppstd(self, 20)

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared with Visual Studio.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_EXPORTED"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "wavelet_buffer")
        self.cpp_info.set_property("cmake_target_name", "wavelet_buffer::wavelet_buffer")
        self.cpp_info.requires = ["blaze::blaze", "cimg::cimg", "streamvbyte::streamvbyte", "fpzip::fpzip"]

        self.cpp_info.libs = ["wavelet_buffer"]

        if self.options.jpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        else:
            self.cpp_info.requires.append("libjpeg::libjpeg")
