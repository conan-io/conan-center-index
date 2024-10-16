from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.0.9"


class RecklessConan(ConanFile):
    name = "reckless"
    description = "Reckless is an extremely low-latency, high-throughput logging library."
    license = "MIT"
    topics = ("logging",)
    homepage = "https://github.com/mattiasflodin/reckless"
    url = "https://github.com/conan-io/conan-center-index"

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

    def validate(self):
        check_min_cppstd(self, 11)
        if self.info.settings.os not in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports Windows and Linux")
        if self.info.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} only supports Visual Studio on Windows")
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")
        # Atomic operations support in reckless requires either libstdc++ or MSVC on an x86 architecture.
        if self.info.settings.compiler == "clang" and self.info.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support clang with libc++")
        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports x86 and x86_64")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RECKLESS_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["reckless"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("synchronization")
