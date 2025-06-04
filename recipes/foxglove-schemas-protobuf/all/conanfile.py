from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
import os


required_conan_version = ">=2.1"


class FoxgloveSchemasProtobufConan(ConanFile):
    name = "foxglove-schemas-protobuf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/foxglove-sdk"
    description = "Protobuf schemas for Foxglove"
    license = "MIT"
    topics = ("foxglove", "protobuf", "schemas")

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    package_type = "library"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=(self.export_sources_folder + "/src"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported yet.")

    def requirements(self):
        self.requires("protobuf/3.21.12", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["foxglove_schemas_protobuf"]
