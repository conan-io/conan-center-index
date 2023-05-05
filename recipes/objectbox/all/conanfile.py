from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class ObjectboxCConan(ConanFile):
    name = "objectbox"
    description = "ObjectBox C and C++: super-fast database for objects and structs"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/objectbox/objectbox-c"
    topics = ("performance", "database", "flatbuffers")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_sync": [True, False],
    }
    default_options = {
        "with_sync": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        tc.variables["OBJECTBOX_WITH_SYNC"] = self.options.with_sync
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["objectbox"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
            if Version(self.version) >= "0.18.0":
                self.cpp_info.system_libs.append("dl")
