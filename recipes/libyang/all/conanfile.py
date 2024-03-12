from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get

required_conan_version = ">=1.53.0"


class LibYangConan(ConanFile):
    name = "libyang"
    license = "BSD-3-Clause license"
    url = "https://github.com/conan-io/conan-center-index"
    description = "YANG data modeling language library"
    homepage = "https://github.com/CESNET/libyang"
    topics = ("yang", "bsd", "netconf", "restconf", "yin")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def requirements(self):
        self.requires("pcre2/10.42", transitive_headers=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "libyang")
        self.cpp_info.libs = ["yang"]
