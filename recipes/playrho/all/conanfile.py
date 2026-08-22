import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rename
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PlayrhoConan(ConanFile):
    name = "playrho"
    description = "Real-time oriented physics engine and library that's currently best suited for 2D games. "
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/louis-langholtz/PlayRho/"
    topics = ("physics-engine", "collision-detection", "box2d")

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
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_versions(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "msvc": "192",
            "Visual Studio": "16",
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_versions.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["PLAYRHO_BUILD_SHARED"] = self.options.shared
        tc.variables["PLAYRHO_BUILD_STATIC"] = not self.options.shared
        tc.variables["PLAYRHO_INSTALL"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "PlayRho"))

    def package_info(self):
        self.cpp_info.libs = ["PlayRho"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.set_property("cmake_file_name", "PlayRho")
        self.cpp_info.set_property("cmake_target_name", "PlayRho::PlayRho")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PlayRho"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PlayRho"
        self.cpp_info.names["cmake_find_package"] = "PlayRho"
        self.cpp_info.names["cmake_find_package_multi"] = "PlayRho"
