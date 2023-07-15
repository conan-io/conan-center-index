from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get


class NetEaseIMConan(ConanFile):
    name = "netease-im"
    description = "NetEase IM cross-platform C++ SDK"
    license = "GNU Public License or the Artistic License"
    homepage = "https://yunxin.163.com/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("im", "nim", "nertc", "netease im", "netease")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_nim": [True, False],
        "with_chatroom": [True, False],
        "with_qchat": [True, False],
        "with_http_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_nim": True,
        "with_chatroom": True,
        "with_qchat": True,
        "with_http_tools": True,
    }
    short_paths = True

    def validate(self):
        if self.settings.os in ["iOS", "Android"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} unsupported platform."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        arch = str(self.settings.arch)
        os = str(self.settings.os)
        get(self, **self.conan_data["sources"][self.version][os][arch])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_CXX_STANDARD"] = "11"
        tc.variables["CMAKE_BUILD_TYPE"] = "Release" if self.settings.build_type == "Release" else "Debug"
        tc.variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="wrapper")
        cmake.build(target="install")

    def package(self):
        if self.settings.os == "Windows":
            self.copy("h_available.dll", "bin", "bin")
            if self.options.with_nim:
                self.copy("nim.dll", "bin", "bin")
            if self.options.with_chatroom:
                self.copy("nim_chatroom.dll", "bin", "bin")
            if self.options.with_qchat:
                self.copy("nim_qchat.dll", "bin", "bin")
            if self.options.with_http_tools:
                self.copy("nim_http_tools.dll", "bin", "bin")
        if self.settings.os == "Linux":
            self.copy("libh_available.so", "lib", "lib")
            if self.options.with_nim:
                self.copy("libnim.so", "lib", "lib")
            if self.options.with_chatroom:
                self.copy("libnim_chatroom.so", "lib", "lib")
            if self.options.with_qchat:
                self.copy("libnim_qchat.so", "lib", "lib")
            if self.options.with_http_tools:
                self.copy("libnim_http_tools.so", "lib", "lib")
        if self.settings.os == "Macos":
            self.copy("libh_available.dylib", "lib", "lib")
            if self.options.with_nim:
                self.copy("libnim.dylib", "lib", "lib")
            if self.options.with_chatroom:
                self.copy("libnim_chatroom.dylib", "lib", "lib")
            if self.options.with_qchat:
                self.copy("libnim_qchat.dylib", "lib", "lib")
            if self.options.with_http_tools:
                self.copy("libnim_http_tools.dylib", "lib", "lib")
        if self.settings.os == "Windows":
            self.copy("*.lib", "lib", "lib")
        if self.settings.os in ["Linux", "Macos"]:
            self.copy("*.a", "lib", "lib", symlinks=True)
        self.copy("*.h", "include", "include")
        self.copy("IntegrationGuide.md", "licenses", "wrapper")

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        library_postfix = ""
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            library_postfix = "_d"
        self.cpp_info.libs.append("nim_wrapper_util{}".format(library_postfix))
        if self.options.with_nim:
            self.cpp_info.libs.append("nim_cpp_wrapper{}".format(library_postfix))
        if self.options.with_chatroom:
            self.cpp_info.libs.append("nim_chatroom_cpp_wrapper{}".format(library_postfix))
        if self.options.with_qchat:
            self.cpp_info.libs.append("nim_qchat_cpp_wrapper{}".format(library_postfix))
        self.cpp_info.frameworks.append("AppKit")
        self.cpp_info.frameworks.append("Foundation")
        self.cpp_info.frameworks.append("SystemConfiguration")
        self.cpp_info.frameworks.append("IOKit")
        self.cpp_info.frameworks.append("CFNetwork")
        self.cpp_info.frameworks.append("CoreGraphics")
        self.cpp_info.frameworks.append("Security")
        self.cpp_info.frameworks.append("CoreServices")
        self.cpp_info.frameworks.append("CoreFoundation")
        self.cpp_info.frameworks.append("CoreText")
