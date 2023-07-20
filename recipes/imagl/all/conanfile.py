import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ImaglConan(ConanFile):
    name = "imagl"
    description = "A lightweight library to load images for OpenGL applications."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Woazim/imaGL"
    topics = ("opengl", "texture", "image")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
    def _compilers_minimum_version(self):
        minimum_versions = {
            "gcc": "9",
            "Visual Studio": "16.2",
            "msvc": "192.2",
            "clang": "10",
            "apple-clang": "11",
        }
        if Version(self.version) <= "0.1.1" or Version(self.version) == "0.2.0":
            minimum_versions["Visual Studio"] = "16.5"
            minimum_versions["msvc"] = "19.25"
        return minimum_versions

    @property
    def _supports_jpeg(self):
        return Version(self.version) >= "0.2.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._supports_jpeg:
            self.options.rm_safe("with_jpeg")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self._supports_jpeg and self.options.with_jpeg:
            self.requires("libjpeg/9e")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)
        # Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(
                "imagl requires some C++20 features, which are available in libc++ for clang compiler."
            )

        compiler_version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("imaGL requires C++20. Your compiler is unknown. Assuming it supports C++20.")
        elif Version(compiler_version) < minimum_version:
            raise ConanInvalidConfiguration(
                "imaGL requires some C++20 features, which your"
                f" {self.settings.compiler} {compiler_version} compiler does not support."
            )
        else:
            print(f"Your compiler is {self.settings.compiler} {compiler_version} and is compatible.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STATIC_LIB"] = not self.options.shared
        tc.variables["SUPPORT_PNG"] = self.options.with_png
        tc.variables["SUPPORT_JPEG"] = self._supports_jpeg and self.options.with_jpeg
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        static_suffix = "" if self.options.shared else "s"
        self.cpp_info.libs = [f"imaGL{debug_suffix}{static_suffix}"]
        if not self.options.shared:
            self.cpp_info.defines = ["IMAGL_STATIC=1"]
