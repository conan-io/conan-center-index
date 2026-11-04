import os

from conan import ConanFile
from conan.tools.build import check_max_cppstd
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rmdir, copy, apply_conandata_patches, export_conandata_patches, rm

required_conan_version = ">=2.0"


class InnoextractConan(ConanFile):
    name = "innoextract"
    description = "Extract contents of Inno Setup installers"
    license = "Zlib"
    topics = ("inno-setup", "decompression")
    homepage = "https://constexpr.org/innoextract"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("libiconv/1.17")

    def validate(self):
        check_max_cppstd(self, "14")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        # Turn off static library detection, which is on by default on Windows.
        # This keeps the CMakeLists.txt from trying to detect static Boost
        # libraries and use Boost components for zlib and BZip2. Getting the
        # libraries via Conan does the correct thing without other assistance.
        tc.variables["USE_STATIC_LIBS"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        rm(self, "FindLZMA.cmake", os.path.join(self.source_folder, "cmake"))
        rm(self, "Findiconv.cmake", os.path.join(self.source_folder, "cmake"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
