from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.0.0"


class XyoSdkConan(ConanFile):
    name = "xyo-sdk"
    description = "Official C++ SDK for XYO Financial - AI Payment Transaction Enrichment"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xyo-financial/sdk-cpp"
    topics = ("banking", "enrichment", "financial", "transactions", "payments")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpr/1.10.5")
        self.requires("nlohmann_json/3.11.3")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("openssl/[>=1.1.1 <4]")

    def validate(self):
        check_min_cppstd(self, "17")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["XYO_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["xyo_sdk"]
        self.cpp_info.set_property("cmake_file_name", "XYOSDK")
        self.cpp_info.set_property("cmake_target_name", "XYO::SDK")
