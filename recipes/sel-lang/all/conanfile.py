from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0.9"


class SelConan(ConanFile):
    name = "sel-lang"
    description = (
        "A small expression language for validation rules that evaluate "
        "identically on PHP, JavaScript, C++ and Common Lisp"
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nathanjel/sel"
    topics = ("expression-language", "validation", "rules", "decimal", "interpreter")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    # No shared option: sel.hpp has no export/visibility macros, so a shared
    # build would not export any symbols on Windows. Upstream's own Conan
    # recipe makes the same call.

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # The harness is upstream's own test rig, not part of the package.
        tc.cache_variables["SEL_BUILD_TOOLS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cpp"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.txt",
             src=os.path.join(self.source_folder, "cpp", "third_party", "srell"),
             dst=os.path.join(self.package_folder, "licenses", "srell"))
        cmake = CMake(self)
        cmake.install()
        # Upstream's own CMake config files duplicate what CMakeDeps generates
        # for consumers, and the CMakeLists also installs its own copy of the
        # licence under share/ alongside the one copied above.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["sel-lang"]
        # Match the names the installed CMake package exports, so
        # find_package(sel-lang) and Conan's generated config agree.
        self.cpp_info.set_property("cmake_file_name", "sel-lang")
        self.cpp_info.set_property("cmake_target_name", "sel-lang::sel-lang")
