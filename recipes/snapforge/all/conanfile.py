from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get

required_conan_version = ">=2.3.0"


class SnapForgeConan(ConanFile):
    name = "snapforge"
    description = "C++17 client for the hosted SnapForge screenshot and page-context API"
    license = "AGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://snapforge.web-tasarimci.com"
    topics = ("screenshot", "rest", "api", "web-client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("libcurl/8.10.1")
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)

    def source(self):
        # Use the published, pinned six-file SDK release, never the private monorepo.
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SNAPFORGE_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SnapForge")
        self.cpp_info.set_property("cmake_target_name", "SnapForge::snapforge")
        self.cpp_info.requires = ["libcurl::curl", "nlohmann_json::nlohmann_json"]
        self.cpp_info.libs = ["snapforge"]
