from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from pathlib import Path

required_conan_version = ">=2.0"


class WebView2SdkConan(ConanFile):
    name = "webview2-sdk"
    description = "Microsoft Edge WebView2 SDK"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.microsoft.com/microsoft-edge/webview2/"
    topics = ("webview2", "webview", "windows", "microsoft")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("webview2-sdk is only available on Windows")

    def package_id(self):
        self.info.settings.rm_safe("compiler")
        self.info.settings.rm_safe("build_type")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def package(self):
        source = Path(self.source_folder)
        include_dir = source / "build" / "native" / "include"
        include_winrt_dir = source / "build" / "native" / "include-winrt"
        lib_dir = source / "build" / "native"

        copy(self, "WebView2.h", src=include_dir, dst=Path(self.package_folder) / "include")
        copy(self, "WebView2EnvironmentOptions.h", src=include_dir, dst=Path(self.package_folder) / "include")
        copy(self, "WebView2Interop.h", src=include_winrt_dir, dst=Path(self.package_folder) / "include-winrt")
        copy(self, "WebView2Interop.idl", src=include_winrt_dir, dst=Path(self.package_folder) / "include-winrt")
        copy(self, "WebView2Interop.tlb", src=include_winrt_dir, dst=Path(self.package_folder) / "include-winrt")

        arch_map = {
            "x86": "x86",
            "x86_64": "x64",
            "armv8": "arm64",
        }
        arch = arch_map.get(str(self.settings.arch))
        if not arch:
            raise ConanInvalidConfiguration(f"Unsupported arch for webview2-sdk: {self.settings.arch}")

        lib_dst = Path(self.package_folder) / "lib"
        bin_dst = Path(self.package_folder) / "bin"
        if self.options.shared:
            copy(self, "WebView2Loader.dll.lib", src=lib_dir / arch, dst=lib_dst)
            copy(self, "WebView2Loader.dll", src=lib_dir / arch, dst=bin_dst)
        else:
            copy(self, "WebView2LoaderStatic.lib", src=lib_dir / arch, dst=lib_dst)

        copy(self, "LICENSE.txt", src=self.source_folder, dst=Path(self.package_folder) / "licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "webview2-sdk")
        self.cpp_info.set_property("cmake_target_name", "webview2-sdk::webview2-sdk")
        self.cpp_info.libs = ["WebView2Loader" if self.options.shared else "WebView2LoaderStatic"]
        self.cpp_info.includedirs = ["include", "include-winrt"]
        self.cpp_info.libdirs = ["lib"]
        if self.options.shared:
            self.cpp_info.bindirs = ["bin"]
