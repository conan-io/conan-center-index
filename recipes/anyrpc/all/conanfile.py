from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.52.0"


class AnyRPCConan(ConanFile):
    name = "anyrpc"
    description = "A multiprotocol remote procedure call system for C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sgieseking/anyrpc"
    topics = ("rpc")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_log4cplus": [True, False],
        "with_threading": [True, False],
        "with_regex": [True, False],
        "with_wchar": [True, False],
        "with_protocol_json": [True, False],
        "with_protocol_xml": [True, False],
        "with_protocol_messagepack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_log4cplus": False,
        "with_threading": True,
        "with_wchar": True,
        "with_regex": True,
        "with_protocol_json": True,
        "with_protocol_xml": True,
        "with_protocol_messagepack": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.0.7")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

        if self.info.options.with_log4cplus and self.info.options.with_wchar:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built with both log4cplus and wchar, see https://github.com/sgieseking/anyrpc/issues/25")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ANYRPC_LIB_BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TEST"] = False
        tc.variables["BUILD_WITH_ADDRESS_SANITIZE"] = False

        tc.variables["BUILD_WITH_LOG4CPLUS"] = self.options.with_log4cplus
        tc.variables["BUILD_WITH_THREADING"] = self.options.with_threading
        tc.variables["BUILD_WITH_REGEX"] = self.options.with_regex
        tc.variables["BUILD_WITH_WCHAR"] = self.options.with_wchar

        tc.variables["BUILD_PROTOCOL_JSON"] = self.options.with_protocol_json
        tc.variables["BUILD_PROTOCOL_XML"] = self.options.with_protocol_xml
        tc.variables["BUILD_PROTOCOL_MESSAGEPACK"] = self.options.with_protocol_messagepack
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="license", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["anyrpc"]
        
        if not self.options.shared and self.settings.os == "Windows":
                self.cpp_info.system_libs.append("ws2_32")
                
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
