import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import download, unzip, get

required_conan_version = ">=1.54"

class DPPConan(ConanFile):
    name = "dpp"
    license = "Apache-2.0"
    package_type = "shared-library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/brainboxdotcc/DPP"
    description = "D++ is a lightweight and efficient library for Discord"
    topics = ("discord")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    @property
    def _min_cppstd(self):
        return 17

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def requirements(self):
        self.requires("nlohmann_json/3.11.2")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("opus/1.4")

    def layout(self):
        cmake_layout(self, src_folder="src")


    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        #zip_name = "DPP.zip"
        #download(self, f"https://github.com/brainboxdotcc/DPP/archive/refs/tags/v{self.version}.zip", zip_name)
        #unzip(self, zip_name, '.', False, None, True)
        #os.unlink(zip_name)
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
  
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CONAN_EXPORTED"] = True
        tc.cache_variables["BUILD_VOICE_SUPPORT"] = True
        tc.cache_variables["DPP_BUILD_TEST"] = False
        tc.cache_variables["BUILD_SHARED_LIBS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dpp"]
        self.cpp_info.includedirs = ["include/dpp-10.0"]
        self.cpp_info.libdirs = ["lib/dpp-10.0"]
    def package_info(self):
        self.cpp_info.libs = ["package_lib"]
        self.cpp_info.set_property("cmake_file_name", "dpp")
        self.cpp_info.set_property("cmake_target_name", "dpp::dpp")

