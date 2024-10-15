import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, get, copy, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.6"


class PackageConan(ConanFile):
    name = "openassetio"
    description = "An open-source interoperability standard for tools and content management systems used in media production."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenAssetIO/OpenAssetIO"
    topics = ("asset-pipeline", "vfx", "cg", "assetmanager", "vfx-pipeline")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_python": [True, False],
    }
    default_options = {
        "shared": False,
        "with_python": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "12",
            "apple-clang": "12",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def configure(self):
        if self.options.with_python and is_msvc(self):
            # Required to create import .lib for building extension module.
            self.options["cpython"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tomlplusplus/3.4.0")
        if self.options.with_python:
            self.requires("cpython/3.12.7")
            self.requires("pybind11/2.13.6")

    def validate(self):
        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support MacOS at this time")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_msvc(self) and not self.dependencies["cpython"].options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} requires cpython:shared=True when using MSVC compiler")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")
        if self.options.with_python:
            self.tool_requires("cpython/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENASSETIO_ENABLE_TESTS"] = False
        tc.variables["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = self.settings.get_safe("compiler.libcxx") == "libstdc++11"
        tc.variables["OPENASSETIO_ENABLE_PYTHON"] = self.options.with_python
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        if self.info.options.with_python:
            self.info.requires["cpython"].minor_mode()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rm(self, "OpenAssetIOConfig*.cmake", os.path.join(self.package_folder, "lib", "cmake", "OpenAssetIO"))
        rm(self, "OpenAssetIOTargets*.cmake", os.path.join(self.package_folder, "lib", "cmake", "OpenAssetIO"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.set_property("cmake_file_name", "OpenAssetIO")
        self.cpp_info.set_property("cmake_target_name", "OpenAssetIO::OpenAssetIO")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "OpenAssetIO", "OpenAssetIOVariables.cmake")])
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]

        self.cpp_info.components["openassetio-core"].set_property("cmake_target_name", "OpenAssetIO::openassetio-core")
        self.cpp_info.components["openassetio-core"].libs = ["openassetio"]

        if self.options.with_python:
            self.cpp_info.components["openassetio-python-bridge"].set_property("cmake_target_name", "OpenAssetIO::openassetio-python-bridge")
            self.cpp_info.components["openassetio-python-bridge"].requires = ["openassetio-core"]
            self.cpp_info.components["openassetio-python-bridge"].libs = ["openassetio-python"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenAssetIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAssetIO"
