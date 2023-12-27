from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.53.0"


class AudiowaveformConan(ConanFile):
    name = "audiowaveform"
    description = "C++ program to generate waveform data and render waveform images from audio files"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://waveform.prototyping.bbc.co.uk/"
    topics = ("audio", "c-plus-plus")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libgd/2.3.3")
        self.requires("libid3tag/0.15.1b")
        self.requires("libmad/0.15.1b")
        self.requires("libsndfile/1.2.2")
        self.requires("boost/1.83.0")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on Visual Studio and msvc.")

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "CMake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
