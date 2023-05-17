from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class LibyuvConan(ConanFile):
    name = "libyuv"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/libyuv/libyuv/"
    description = "libyuv is an open source project that includes YUV scaling and conversion functionality."
    topics = ["YUV", "libyuv", "google", "chromium"]
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
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
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.1")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            # Injecting CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS is not sufficient since there are global symbols
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported for msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TEST"] = False
        tc.variables["LIBYUV_WITH_JPEG"] = bool(self.options.with_jpeg)
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

    def package_info(self):
        self.cpp_info.libs = ["yuv"]
        self.cpp_info.requires = []
        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.requires.append("mozjpeg::libjpeg")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
