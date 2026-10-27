from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, download, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
import os

required_conan_version = ">=2.4"


class StormlibConan(ConanFile):
    name = "stormlib"
    description = "StormLib is a library for reading and writing MPQ archives used in Blizzard games."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ladislav-zezula/StormLib"
    topics = ("mpq", "archive", "blizzard")
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

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("bzip2/1.0.8")
        self.requires("libtommath/1.3.0")

    def validate(self):
        if self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("Macos framework libs upstream installation is not complete")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 11)", "")
        apply_conandata_patches(self)
        # The recipe vendorizes libtomcrypt, copy its license for later repackaging
        download(self,
                 url="https://raw.githubusercontent.com/libtom/libtomcrypt/a68fa19bc2b532f66a6f18ca457daec53054a312/LICENSE",
                 filename=os.path.join(self.source_folder, "LICENSE-thirdparty-libtomcrypt"),
                 sha256="2fa64b163659f41965c9815882a8296d3d03ff546b76153e11445f9bdecf955a")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["STORM_USE_BUNDLED_LIBRARIES"] = False
        tc.cache_variables["STORM_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-thirdparty-libtomcrypt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "StormLib")
        self.cpp_info.set_property("cmake_target_name", "StormLib::storm")

        libname = "storm"
        if self.settings.os == "Windows":
            libname = "StormLib"
            # Disabled #pragma comment(lib, "StormLib{R/D}A{S/D}.lib")
            self.cpp_info.defines.append("__STORMLIB_NO_STATIC_LINK__")
            self.cpp_info.system_libs = ["wininet"]
        self.cpp_info.libs = [libname]
