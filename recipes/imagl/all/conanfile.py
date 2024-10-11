from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class ImaglConan(ConanFile):
    name = "imagl"
    license = "LGPL-3.0-only"
    homepage = "https://github.com/Woazim/imaGL"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A lightweight library to load image for OpenGL application."
    topics = ("opengl", "texture", "image")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jpeg": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_jpeg": True,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
                "gcc": "9",
                "clang": "10",
                "apple-clang": "11"
        }

    @property
    def _supports_jpeg(self):
        return Version(self.version) >= "0.2.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if not self._supports_jpeg:
            self.options.rm_safe("with_jpeg")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self._supports_jpeg and self.options.with_jpeg:
            self.requires("libjpeg/9e")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        # INFO: Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.get_safe("compiler.libcxx") != "libc++":
            raise ConanInvalidConfiguration("imagl requires some C++20 features, which are available in libc++ for clang compiler.")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["STATIC_LIB"] = not self.options.shared
        tc.variables["SUPPORT_PNG"] = self.options.with_png
        if self._supports_jpeg:
            tc.variables["SUPPORT_JPEG"] = self.options.with_jpeg
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        static_suffix = "" if self.options.shared else "s"
        self.cpp_info.libs = [f"imaGL{debug_suffix}{static_suffix}"]
        if not self.options.shared:
            self.cpp_info.defines = ["IMAGL_STATIC=1"]
