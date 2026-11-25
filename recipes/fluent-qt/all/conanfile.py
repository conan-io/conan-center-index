import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.11"


class FluentQtConan(ConanFile):
    name = "fluent-qt"
    description = "Fluent UI components for native Qt Widgets desktop applications."
    license = "MIT", "OFL-1.1"
    homepage = "https://github.com/calvinhxx/Fluent-Qt"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("qt", "widgets", "gui", "fluent-design")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.2 <7]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        if cross_building(self):
            self.tool_requires("qt/<host_version>")
            self.tool_requires("cmake/[>=3.27 <4]")
        else:
            self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        if self.settings.os not in ("Macos", "Linux", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} supports macOS, Linux and Windows")
        check_min_cppstd(self, 17)
        if not self.dependencies["qt"].options.widgets:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:widgets=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_INSTALL_LIBDIR"] = "lib"
        tc.cache_variables["FLUENT_QT_BUILD_EXAMPLES"] = False
        tc.cache_variables["FLUENT_QT_DEBUG_RELEASE_RUNTIME"] = False
        if cross_building(self):
            tools_dir = self.conf.get("user.qt:tools_directory", check_type=str)
            ext = ".exe" if self.settings_build.os == "Windows" else ""
            tc.cache_variables["CMAKE_AUTOMOC_EXECUTABLE"] = os.path.join(tools_dir, "moc" + ext)
            tc.cache_variables["CMAKE_AUTORCC_EXECUTABLE"] = os.path.join(tools_dir, "rcc" + ext)
        else:
            VirtualRunEnv(self).generate(scope="build")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        CMake(self).install(component="Development")
        share = os.path.join(self.package_folder, "share")
        copy(self, "*", os.path.join(share, "licenses", "FluentQt"),
             os.path.join(self.package_folder, "licenses"))
        rmdir(self, share)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "FluentQt")
        self.cpp_info.set_property("cmake_target_name", "FluentQt::FluentQt")
        self.cpp_info.libs = ["FluentQt"]
        self.cpp_info.requires = ["qt::qtWidgets"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "FluentQt")]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreGraphics"]
            self.cpp_info.system_libs = ["objc"]
