from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "cppdap"
    description = "Debug Adapter Protocol SDK"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cppdap"
    topics = ("debug", "adapter", "protocol", "dap")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_json": ["jsoncpp", "nlohmann_json", "rapidjson"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_json": "nlohmann_json",
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_json == "jsoncpp":
            self.requires("jsoncpp/1.9.5")
        elif self.options.with_json == "rapidjson":
            self.requires("rapidjson/cci.20220822")        
        elif self.options.with_json == "nlohmann_json":
            self.requires("nlohmann_json/3.11.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CPPDAP_USE_EXTERNAL_JSONCPP_PACKAGE"] = self.options.with_json == "jsoncpp"
        tc.variables["CPPDAP_USE_EXTERNAL_RAPIDJSON_PACKAGE"] = self.options.with_json == "rapidjson"
        tc.variables["CPPDAP_USE_EXTERNAL_NLOHMANN_JSON_PACKAGE"] = self.options.with_json == "nlohmann_json"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["cppdap"]

        self.cpp_info.set_property("cmake_file_name", "cppdap")
        self.cpp_info.set_property("cmake_target_name", "cppdap::cppdap")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os in ["Windows"]:
            self.cpp_info.system_libs.append("ws2_32")
