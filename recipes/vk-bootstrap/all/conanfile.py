from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class VkBootstrapConan(ConanFile):
    name = "vk-bootstrap"
    description = "Vulkan bootstraping library."
    license = "MIT"
    topics = ("vulkan", "bootstrap", "setup")
    homepage = "https://github.com/charles-lunarg/vk-bootstrap"
    url = "https://github.com/conan-io/conan-center-index"

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
        if Version(self.version) >= "1.3.270":
            return 17
        return 14

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) >= "1.3.270":
            return {
                "gcc": "7",
                "Visual Studio": "15",
                "msvc": "191",
                "clang": "6",
                "apple-clang": "11",
            }
        else:
            return {
                "gcc": "5",
                "Visual Studio": "15",
                "msvc": "191",
                "clang": "3.7" if stdcpp_library(self) == "stdc++" else "6",
                "apple-clang": "10",
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

    @property
    def _headers_version(self):
        return {}.get(self.version, f"{self.version}.0")

    def requirements(self):
        if Version(self.version) >= "1.3":
            self.requires(f"vulkan-headers/{self._headers_version}", transitive_headers=True)
        elif Version(self.version) >= "0.7":
            self.requires("vulkan-headers/1.3.239.0", transitive_headers=True)
        else:
            self.requires("vulkan-headers/1.3.236.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VK_BOOTSTRAP_TEST"] = False
        vulkan_headers = self.dependencies["vulkan-headers"]
        includedirs = ";".join(
            os.path.join(vulkan_headers.package_folder, includedir).replace("\\", "/")
            for includedir in vulkan_headers.cpp_info.includedirs
        )
        if Version(self.version) < "0.3.0":
            tc.variables["Vulkan_INCLUDE_DIR"] = includedirs
        else:
            tc.variables["VK_BOOTSTRAP_VULKAN_HEADER_DIR"] = includedirs
        if Version(self.version) >= "0.4.0":
            tc.variables["VK_BOOTSTRAP_WERROR"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["vk-bootstrap"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]
