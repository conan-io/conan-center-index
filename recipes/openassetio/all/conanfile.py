from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, get, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "openassetio"
    description = "An open-source interoperability standard for tools and content management systems used in media production."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenAssetIO/OpenAssetIO"
    topics = ("asset-pipeline", "vfx", "cg", "assetmanager", "vfx-pipeline")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "without_python": [True, False],
        "python_version": ["3.7.12", "3.8.12", "3.9.7", "3.10.0"]
    }
    default_options = {
        "shared": False,
        "without_python": False,
        "python_version": "3.9.7"
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "apple-clang": "12",
        }

    def configure(self):
        if self.options.without_python:
            self.options.rm_safe("python_version")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if not self.options.without_python:
            self.requires(f"cpython/{self.options.python_version}")
            self.requires("pybind11/2.10.0")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def build_requirements(self):
        self.tool_requires("tomlplusplus/3.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["OPENASSETIO_ENABLE_TESTS"] = not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx is not None:
            if libcxx == "libstdc++11":
                tc.variables["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = True
            else:
                tc.variables["OPENASSETIO_GLIBCXX_USE_CXX11_ABI"] = False

        if self.options.without_python:
            tc.variables["OPENASSETIO_ENABLE_PYTHON"] = False
        else:
            tc.variables["OPENASSETIO_ENABLE_PYTHON"] = True
            tc.variables["Python_EXECUTABLE"] = self._python_exe
            if self.settings.os == "Windows":
                tc.variables["Python_LIBRARY"] = self._python_lib

        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    @property
    def _python_exe(self):
        return self.deps_user_info["cpython"].python

    @property
    def _python_lib(self):
        return os.path.join(
            self.dependencies["cpython"].cpp_info.rootpath,
            self.dependencies["cpython"].cpp_info.components["embed"].libdirs[0],
            self.dependencies["cpython"].cpp_info.components["embed"].libs[0])

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        if not self.options.without_python:
            self.info.requires["cpython"].minor_mode()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rm(self, "OpenAssetIOConfig*.cmake", os.path.join(self.package_folder, "lib", "cmake", "OpenAssetIO"))
        rm(self, "OpenAssetIOTargets*.cmake", os.path.join(self.package_folder, "lib", "cmake", "OpenAssetIO"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]
        self.cpp_info.set_property("cmake_file_name", "OpenAssetIO")
        self.cpp_info.set_property("cmake_target_name", "OpenAssetIO::OpenAssetIO")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "OpenAssetIO", "OpenAssetIOVariables.cmake")])
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]

        self.cpp_info.components["openassetio-core"].set_property("cmake_target_name", "OpenAssetIO::openassetio-core")
        self.cpp_info.components["openassetio-core"].libs = ["openassetio"]
        self.cpp_info.components["openassetio-core-c"].set_property("cmake_target_name", "OpenAssetIO::openassetio-core-c")
        self.cpp_info.components["openassetio-core-c"].requires = ["openassetio-core"]
        self.cpp_info.components["openassetio-core-c"].libs = ["openassetio-c"]
        if not self.options.shared and self._stdcpp_library:
            self.cpp_info.components["openassetio-core-c"].system_libs.append(self._stdcpp_library)
        if not self.options.without_python:
            self.cpp_info.components["openassetio-python-bridge"].set_property("cmake_target_name", "OpenAssetIO::openassetio-python-bridge")
            self.cpp_info.components["openassetio-python-bridge"].requires = ["openassetio-core"]
            self.cpp_info.components["openassetio-python-bridge"].libs = ["openassetio-python"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenAssetIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAssetIO"

    @property
    def _stdcpp_library(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ("libstdc++", "libstdc++11"):
            return "stdc++"
        elif libcxx in ("libc++",):
            return "c++"
        return False
