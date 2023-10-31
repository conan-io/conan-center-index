from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
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

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "8",
            "clang": "12",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
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
        self.requires("cimg/3.2.5")
        if self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        else:
            self.requires("libjpeg/9e")
        # FIXME: unvendor SfCompressor which is currently downloaded at build time :s
        if Version(self.version) >= "0.6.0":
            self.requires("streamvbyte/1.0.0")
            self.requires("fpzip/1.3.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

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
        self.cpp_info.requires = ["blaze::blaze", "cimg::cimg"]
        if Version(self.version) >= "0.6.0":
            self.cpp_info.libs = ["wavelet_buffer"]
            self.cpp_info.requires.extend(["streamvbyte::streamvbyte", "fpzip::fpzip"])
        else:
            self.cpp_info.libs = ["wavelet_buffer", "sf_compressor"]
        if self.options.jpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        else:
            self.cpp_info.requires.append("libjpeg::libjpeg")
