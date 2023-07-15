from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
import os


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
        if self.settings.os not in ["Linux", "Windows", "Macos"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} unsupported platform."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["All"])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_CXX_STANDARD"] = "11"
        tc.variables["CMAKE_BUILD_TYPE"] = "Release" if self.settings.build_type == "Release" else "Debug"
        tc.variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.generate()

    def build(self):
        get(self, **self.conan_data["sources"][self.version]
            [str(self.settings.os)][str(self.settings.arch)])
        cmake = CMake(self)
        cmake.configure(build_script_folder="wrapper")
        cmake.build(target="install")

    def package(self):
        src_lib_folder = os.path.join(self.build_folder, "lib")
        dst_lib_folder = os.path.join(self.package_folder, "lib")
        src_bin_folder = os.path.join(self.build_folder, "bin")
        dst_bin_folder = os.path.join(self.package_folder, "bin")
        src_include_folder = os.path.join(self.build_folder, "include")
        dst_include_folder = os.path.join(self.package_folder, "include")
        if self.settings.os == "Windows":
            copy(self, "h_available.dll", dst=dst_bin_folder, src=src_bin_folder)
            if self.options.with_nim:
                copy(self, "nim.dll", dst=dst_bin_folder, src=src_bin_folder)
            if self.options.with_chatroom:
                copy(self, "nim_chatroom.dll",
                     dst=dst_bin_folder, src=src_bin_folder)
            if self.options.with_qchat:
                copy(self, "nim_qchat.dll", dst=dst_bin_folder, src=src_bin_folder)
            if self.options.with_http_tools:
                copy(self, "nim_http_tools.dll",
                     dst=dst_bin_folder, src=src_bin_folder)
        if self.settings.os == "Linux":
            copy(self, "*.*", dst=dst_lib_folder, src=src_lib_folder)
        if self.settings.os == "Macos":
            copy(self, "libh_available.dylib", dst=os.path.join(
                self.package_folder, "lib"), src=os.path.join(self.source_folder, "lib"))
            if self.options.with_nim:
                copy(self, "libnim.dylib", dst=dst_lib_folder, src=src_lib_folder)
            if self.options.with_chatroom:
                copy(self, "libnim_chatroom.dylib",
                     dst=dst_lib_folder, src=src_lib_folder)
            if self.options.with_qchat:
                copy(self, "libnim_qchat.dylib",
                     dst=dst_lib_folder, src=src_lib_folder)
            if self.options.with_http_tools:
                copy(self, "libnim_http_tools.dylib",
                     dst=dst_lib_folder, src=src_lib_folder)
        if self.settings.os == "Windows":
            copy(self, "*.lib", dst=dst_lib_folder, src=src_lib_folder)
        if self.settings.os in ["Linux", "Macos"]:
            copy(self, "*.a", dst=dst_lib_folder,
                 src=src_lib_folder)
        copy(self, "*.h", dst=dst_include_folder, src=src_include_folder)
        copy(self, "IntegrationGuide.md", dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.build_folder, "wrapper"))

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        library_postfix = ""
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            library_postfix = "_d"
        self.cpp_info.libs.append("nim_wrapper_util{}".format(library_postfix))
        if self.options.with_nim:
            self.cpp_info.libs.append(
                "nim_cpp_wrapper{}".format(library_postfix))
        if self.options.with_chatroom:
            self.cpp_info.libs.append(
                "nim_chatroom_cpp_wrapper{}".format(library_postfix))
        if self.options.with_qchat:
            self.cpp_info.libs.append(
                "nim_qchat_cpp_wrapper{}".format(library_postfix))

        if self.settings.os == "Macos":
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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
            self.cpp_info.system_libs.append("rt")
            self.cpp_info.system_libs.append("m")
