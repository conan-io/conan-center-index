from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, mkdir
import os
import shutil

required_conan_version = ">=2.0.9"


class CineformConan(ConanFile):
    name = "cineform-sdk"
    description = "The GoPro CineForm video codec SDK"
    license = "Apache-2.0, MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gopro/cineform-sdk"
    topics = ("compression", "sdk", "gopro", "wavelet", "wavelets", "cineform")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_separated": [True, False],
        "enable_tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_separated": False,
        "enable_tools": True
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Linux" and self.options.shared:
            self.requires("libuuid/1.0.3", transitive_libs=True)

    def validate(self):
        if self.settings.arch not in ["x86_64"]:
            raise ConanInvalidConfiguration(
                "{}/{} supported only on x86_64 arch".format(self.name, self.version))

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.5.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TOOLS"] = self.options.enable_tools
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SEPARATED"] = self.options.enable_separated
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-APACHE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure(variables={
            "CMAKE_INSTALL_PREFIX": self.package_folder
        })
        cmake.install()
        postfix = ".exe" if self.settings.os == "Windows" else ""

        if self.options.enable_tools:
            copy(self, "*TestCFHD"+postfix, src=self.build_folder,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*WaveletDemo"+postfix, src=self.build_folder,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared and self.settings.os == "Windows":
            mkdir(self, os.path.join(self.package_folder, "bin"))
            if self.options.enable_separated:
                shutil.move(os.path.join(self.package_folder, "lib", "CFHDDecoder.dll"), os.path.join(
                    self.package_folder, "bin", "CFHDDecoder.dll"))
                shutil.move(os.path.join(self.package_folder, "lib", "CFHDEncoder.dll"), os.path.join(
                    self.package_folder, "bin", "CFHDEncoder.dll"))
            else:
                shutil.move(os.path.join(self.package_folder, "lib", "CFHDCodec.dll"), os.path.join(
                    self.package_folder, "bin", "CFHDCodec.dll"))

    def package_info(self):
        postfix = ""
        requires = []

        if not self.options.shared:
            postfix = "Static" if self.settings.os == "Windows" or self.options.enable_separated else ""

        if self.settings.os == "Linux" and self.options.shared:
            requires = ["libuuid::libuuid"]

        if not self.options.enable_separated:
            self.cpp_info.libs = ["CFHDCodec"+postfix]
        else:
            self.cpp_info.components["decoder"].libs = ["CFHDDecoder"+postfix]
            self.cpp_info.components["decoder"].requires = requires
            self.cpp_info.components["encoder"].libs = ["CFHDEncoder"+postfix]
            self.cpp_info.components["encoder"].requires = requires
