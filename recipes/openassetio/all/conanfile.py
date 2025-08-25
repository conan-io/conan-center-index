import os

from conan import ConanFile
from conan.tools.microsoft import check_min_vs
from conan.tools.files import get, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv


required_conan_version = ">=2.0.9"


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
        "fPIC": [True, False],
        "with_python": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_python": True,
    }
    implements = ["auto_shared_fpic"]
    short_paths = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tomlplusplus/3.2.0")
        self.requires("ada/2.7.4")
        self.requires("pcre2/10.42")
        self.requires("fmt/9.1.0", options={"header_only": True})
        if self.options.with_python:
            self.requires("pybind11/2.10.4")
            # self.requires("cpython/3.12.7")

    def validate(self):
        check_min_cppstd(self, 17)
        check_min_vs(self, 191)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()

        tc = CMakeToolchain(self)
        tc.variables["OPENASSETIO_ENABLE_TESTS"] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)
        tc.variables["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = self.settings.get_safe("compiler.libcxx") == "libstdc++11"
        tc.variables["OPENASSETIO_ENABLE_PYTHON"] = self.options.with_python
        if self.options.with_python:
            tc.cache_variables["OPENASSETIO_ENABLE_PYTHON_STUBGEN"] = False
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
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
