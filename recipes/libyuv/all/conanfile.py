from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
import os

required_conan_version = ">=1.47.0"


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
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5")

    def validate(self):
        if self.info.options.with_jpeg == "libjpeg-turbo":
            raise ConanInvalidConfiguration(
                "libjpeg-turbo is an invalid option right now, as it is not supported by the cmake script.",
            )

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

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
