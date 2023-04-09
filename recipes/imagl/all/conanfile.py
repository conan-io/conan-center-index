from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class ImaglConan(ConanFile):
    name = "imagl"
    license = "lgpl-3.0-only"
    homepage = "https://gitlab-lepuy.iut.uca.fr/opengl/imagl"
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
    _cmake = None

    @property
    def _compilers_minimum_version(self):
        minimum_versions = {
                "gcc": "9",
                "Visual Studio": "16.2",
                "msvc": "19.22",
                "clang": "10",
                "apple-clang": "11"
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
            self.requires("libpng/1.6.37")
        if self._supports_jpeg and self.options.with_jpeg:
            self.requires("libjpeg/9d")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 20)
        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        #Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.get_safe("compiler.libcxx") != "libc++":
            raise ConanInvalidConfiguration("imagl requires some C++20 features, which are available in libc++ for clang compiler.")

        compiler_version = str(self.settings.get_safe("compiler.version"))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("imaGL requires C++20. Your compiler is unknown. Assuming it supports C++20.")
        elif lazy_lt_semver(compiler_version, minimum_version):
            raise ConanInvalidConfiguration("imaGL requires some C++20 features, which your {} {} compiler does not support.".format(str(self.settings.compiler), compiler_version))
        else:
            print("Your compiler is {} {} and is compatible.".format(str(self.settings.compiler), compiler_version))

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
        self.cpp_info.libs = ["imaGL{}{}".format(debug_suffix, static_suffix)]
        if not self.options.shared:
            self.cpp_info.defines = ["IMAGL_STATIC=1"]

