from os import path
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

required_conan_version = ">=1.53.0"


class GKlibConan(ConanFile):
    name = "gklib"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KarypisLab/GKlib"
    description = "A library of various helper routines and frameworks" \
                  " used by many of the lab's software"
    topics = ("karypislab")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} shared not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["ASSERT"] = self.settings.build_type == "Debug"
        tc.variables["ASSERT2"] = self.settings.build_type == "Debug"

        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", src=self.source_folder,
             dst=path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["GKlib"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if is_msvc(self) or self._is_mingw:
            self.cpp_info.defines.append("USE_GKREGEX")
        if is_msvc(self):
            self.cpp_info.defines.append("__thread=__declspec(thread)")
