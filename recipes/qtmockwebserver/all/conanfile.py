from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake
from os import path

class QtMockWebServerConan(ConanFile):
    name = "qtmockwebserver"
    license = "Apache-2.0"
    homepage = "https://github.com/ArchangelSDY/QtMockWebServer"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A simple mock web server built on top of Qt."
    topics = ("Qt", "mock", "webserver")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Macos", "iOS", "tvOS", "watchOS"]:
            self.requires("qt/[>=5.9 <6]")
        else:
            self.requires("qt/[>=5.9 <7]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="*.h",  src=self.source_folder, dst=path.join(self.package_folder, "include/qtmockwebserver"), keep_path=False)
        copy(self, pattern="*.a", src=self.build_folder,  dst=path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.lib",  src=self.build_folder, dst=path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["qtmockwebserver"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork"]
