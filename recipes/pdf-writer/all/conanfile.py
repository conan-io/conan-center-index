from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.gnu import PkgConfigDeps
import os

required_conan_version = ">=1.53.0"

class PDFWriterConan(ConanFile):
    name = "pdf-writer"
    description = "High performance library for creating, modiyfing and parsing PDF files in C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/galkahana/PDF-Writer"
    topics = ("pdf", "writer")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_jpeg": True,
        "with_tiff": True,
    }

    @property
    def _min_cppstd(self):
        return 11

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
        self.requires("freetype/2.13.0")
        self.requires("libaesgm/2013.1.1")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_png:
            self.requires("libjpeg/9e")
        if self.options.with_jpeg:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_BUNDLED"] = False
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PDFHummus")
        self.cpp_info.set_property("cmake_target_name", "PDFHummus::PDFWriter")
        self.cpp_info.libs = ["PDFWriter"]
        self.cpp_info.requires = ["freetype::freetype", "zlib::zlib", "libaesgm::libaesgm"]
        if self.options.with_png:
            self.cpp_info.requires.append("libjpeg::libjpeg")
        if self.options.with_jpeg:
            self.cpp_info.requires.append("libpng::libpng")
        if self.options.with_tiff:
            self.cpp_info.requires.append("libtiff::libtiff")
