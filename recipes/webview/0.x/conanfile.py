import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2"


class WebviewConan(ConanFile):
    name = "webview"
    version = "0.12.0"
    description = "A tiny cross-platform webview library for C/C++ to build modern cross-platform GUIs."
    license = "MIT"
    homepage = "https://github.com/webview/webview"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("webview", "gui", "web", "browser")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    package_type = "library"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("gtk/system", options={"gtk/*:version": "3"})
            self.requires("webkit2gtk/system")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WEBVIEW_BUILD"] = True
        tc.variables["WEBVIEW_BUILD_SHARED_LIBRARY"] = self.options.shared
        tc.variables["WEBVIEW_BUILD_STATIC_LIBRARY"] = not self.options.shared
        tc.variables["WEBVIEW_BUILD_TESTS"] = False
        tc.variables["WEBVIEW_BUILD_EXAMPLES"] = False
        tc.variables["WEBVIEW_BUILD_DOCS"] = False
        tc.variables["WEBVIEW_INSTALL_DOCS"] = False
        tc.variables["WEBVIEW_ENABLE_PACKAGING"] = False
        tc.variables["WEBVIEW_ENABLE_CHECKS"] = False
        tc.variables["WEBVIEW_USE_COMPAT_MINGW"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="webview_core_shared" if self.options.shared else "webview_core_static")

    def package(self):
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows":
            webview2_include = os.path.join(
                self.build_folder,
                "_deps",
                "microsoft_web_webview2-src",
                "build",
                "native",
                "include",
            )
            copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=webview2_include)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        c_api = self.cpp_info.components["c_api"]
        c_api.set_property("cmake_target_name", "webview::c_api")
        library = "webview"
        if not self.options.shared and self.settings.compiler == "msvc":
            library = "webview_static"
        if self.settings.build_type == "Debug":
            library += "d"
        c_api.libs = [library]
        c_api.libdirs = ["lib"]
        c_api.defines = ["WEBVIEW_HEADER", "WEBVIEW_SHARED" if self.options.shared else "WEBVIEW_STATIC"]
        if self.settings.os == "Windows":
            c_api.system_libs = ["advapi32", "ole32", "shell32", "shlwapi", "user32", "version"]
        elif self.settings.os == "Linux":
            c_api.requires = ["gtk::gtk", "webkit2gtk::webkit2gtk"]
            c_api.system_libs.append("dl")
            c_api.includedirs.append("include")
            c_api.libdirs = ["lib"]
        elif self.settings.os == "Macos":
            c_api.frameworks = ["Cocoa", "WebKit"]
        self.cpp_info.libdirs = ["lib"]
