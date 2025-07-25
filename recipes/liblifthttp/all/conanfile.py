from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.9"

class LiftHttpConan(ConanFile):
    name = "lifthttp"
    description = "Safe and easy to use C++17 HTTP client library."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbaldwin/liblifthttp"
    topics = ("cpp", "async", "asynchronous", "http", "https", "web", "client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "PIE": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "PIE": False,
    }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.88.1 <9]", transitive_headers=True)
        self.requires("libuv/[>=1 <2]", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_lifthttp_INCLUDE"] = "conan_deps.cmake"
        tc.variables["LIFT_BUILD_EXAMPLES"] = False
        tc.variables["LIFT_BUILD_TESTS"] = False
        tc.variables["LIFT_USER_LINK_LIBRARIES"] = "CURL::libcurl;uv"
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["LIFT_USER_LINK_LIBRARIES"] += ";pthread;dl"
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "inc"), dst=os.path.join(self.package_folder, "include"))
        for pattern in ["*.a", "*.so*", "*.dylib", "*.lib"]:
            copy(self, pattern, src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "lifthttp")
        self.cpp_info.set_property("cmake_target_name", "lifthttp::lifthttp")
        self.cpp_info.libs = ["lifthttp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "stdc++fs"])
