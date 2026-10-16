from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class CausalontologyConan(ConanFile):
    name = "causalontology"
    description = (
        "The C++ binding of the Causalontology standard - reified causation "
        "as a language-neutral standard and shared commons. Zero dependencies; "
        "passes all 38 frozen conformance vectors."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ai-university-aiu/causalontology"
    topics = ("causality", "ontology", "knowledge-representation", "json", "content-addressing")
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
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        # The CMake project lives in the bindings/cpp subdirectory of the repository
        cmake.configure(build_script_folder=os.path.join("bindings", "cpp"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["causalontology"]
        self.cpp_info.set_property("cmake_file_name", "causalontology")
        self.cpp_info.set_property("cmake_target_name", "causalontology::causalontology")
