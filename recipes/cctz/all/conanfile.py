from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class CCTZConan(ConanFile):
    name = "cctz"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cctz"
    description = "C++ library for translating between absolute and civil times"
    topics = ("cctz", "time", "timezones")
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_tools" : [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "build_tools": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler == "Visual Studio" and \
           Version(self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("CCTZ requires MSVC >= 14")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TOOLS"] = self.options.build_tools
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        # For shared msvc
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cctz")
        self.cpp_info.set_property("cmake_target_name", "cctz::cctz")
        self.cpp_info.libs = ["cctz"]
        if tools_legacy.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")

        if self.options.build_tools:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
