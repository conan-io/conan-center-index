import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class WebbridgeConan(ConanFile):
    name = "webbridge"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WebBridge-Project/webbridge-runtime"
    description = (
        "C++ to JavaScript bridge for building WebView2-based desktop UIs "
        "with Qt-like properties/methods/events and no boilerplate."
    )
    topics = ("webview", "gui", "javascript", "codegen")
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"with_webview": [True, False]}
    default_options = {"with_webview": False}

    def validate(self):
        if self.options.with_webview and self.settings.os != "Windows":
            raise ConanInvalidConfiguration(
                "webbridge's webview integration relies on Microsoft WebView2 and is Windows-only; "
                "set with_webview=False to use the rest of the library on other platforms."
            )

    def requirements(self):
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["webbridge"], strip_root=True)

    def generate(self):
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)
        tc.variables["WEBBRIDGE_WITH_WEBVIEW"] = bool(self.options.with_webview)
        tc.generate()

    def build(self):
        # Not in source(): that method can't access self.options (source code
        # must be option-invariant), but whether we vendor webview/webview2 at
        # all is exactly the thing with_webview controls.
        if self.options.with_webview:
            data = self.conan_data["sources"][self.version]
            get(self, **data["webview"], destination=os.path.join(self.source_folder, "vendor", "webview"), strip_root=True)
            get(self, **data["webview2"], destination=os.path.join(self.source_folder, "vendor", "webview2"), filename="webview2.zip")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "THIRD-PARTY-NOTICES.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "src", "webbridge"),
             dst=os.path.join(self.package_folder, "include", "webbridge"))
        # *.lib (MSVC) and *.a (GCC/Clang on Linux/macOS) - static library naming differs by platform.
        copy(self, "*.lib", src=self.build_folder,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        if self.options.with_webview:
            copy(self, "webbridge-webview.cmake",
                 src=os.path.join(self.source_folder, "cmake"),
                 dst=os.path.join(self.package_folder, "cmake"))
            copy(self, "*", src=os.path.join(self.source_folder, "vendor", "webview"),
                 dst=os.path.join(self.package_folder, "vendor", "webview"))
            copy(self, "*", src=os.path.join(self.source_folder, "vendor", "webview2"),
                 dst=os.path.join(self.package_folder, "vendor", "webview2"))

    def package_info(self):
        self.cpp_info.libs = ["webbridge"]
        self.cpp_info.set_property("cmake_target_name", "webbridge::webbridge")
        if self.options.with_webview:
            self.cpp_info.defines = ["_WIN32_WINNT=0x0A00", "WEBBRIDGE_WITH_WEBVIEW"]
            self.cpp_info.builddirs = ["cmake"]
            self.cpp_info.set_property("cmake_build_modules", [os.path.join("cmake", "webbridge-webview.cmake")])
