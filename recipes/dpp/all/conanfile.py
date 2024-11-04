import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2"

class DPPConan(ConanFile):
    name = "dpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/brainboxdotcc/DPP"
    description = "D++ is a lightweight and efficient library for Discord"
    topics = ("discord")
    package_type = "shared-library"
    settings = "os", "compiler", "build_type", "arch"

    def validate(self):
        check_min_cppstd(self, "17")

    def requirements(self):
        self.requires("nlohmann_json/3.11.2", transitive_libs=True, transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("opus/1.4")

    def layout(self):
        cmake_layout(self, src_folder="src")


    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
  
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["DPP_NO_VCPKG"] = True
        tc.cache_variables["DPP_USE_EXTERNAL_JSON"] = True
        tc.cache_variables["CONAN_EXPORTED"] = True
        tc.cache_variables["BUILD_VOICE_SUPPORT"] = True
        tc.cache_variables["DPP_BUILD_TEST"] = False
        tc.cache_variables["BUILD_SHARED_LIBS"] = True
        if Version(self.version) <= "10.0.34":
            # Workaround for Neon not compiling in old versions
            tc.cache_variables["AVX_TYPE"] = "AVX0"
        if self.settings.os == "Macos" and cross_building(self) and self.settings.arch == "x86_64":
            tc.cache_variables["AVX1_EXITCODE"] = "0"
            tc.cache_variables["AVX2_EXITCODE"] = "0"
            tc.cache_variables["AVX512_EXITCODE"] = "-1"
            tc.cache_variables["AVX1024_EXITCODE"] = "-1"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["dpp"]
        self.cpp_info.set_property("cmake_file_name", "dpp")
        self.cpp_info.set_property("cmake_target_name", "dpp::dpp")
        # On windows only, the headers and libs go into dpp-10.0 subdirectories.
        if self.settings.os == "Windows":
            self.cpp_info.includedirs = ["include/dpp-10.0"]
            self.cpp_info.libdirs = ["lib/dpp-10.0"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.defines = ["DPP_USE_EXTERNAL_JSON"]
