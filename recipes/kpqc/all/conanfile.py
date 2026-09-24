import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir


required_conan_version = ">=2.4"


class KpqcConan(ConanFile):
    name = "kpqc"
    description = "C++ APIs for AIMer, HAETAE, NTRU+, and SMAUG-T"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KpqC/kpqc-cpp"
    topics = ("post-quantum-cryptography", "cryptography", "kem", "digital-signature")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    languages = "C", "C++"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["KPQC_BUILD_TESTS"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "THIRD_PARTY_NOTICES.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        for component in ("AIMer", "HAETAE", "NTRUplus", "SMAUG-T"):
            copy(
                self,
                "LICENSE",
                os.path.join(self.source_folder, "vendor", component),
                os.path.join(self.package_folder, "licenses", component),
            )

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["kpqc"]
        self.cpp_info.set_property("cmake_file_name", "kpqc")
        self.cpp_info.set_property("cmake_target_name", "kpqc::kpqc")
        if self.settings.os in ("Linux", "FreeBSD", "Android"):
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("bcrypt")
