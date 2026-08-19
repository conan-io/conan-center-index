from conan import ConanFile
from conan.tools.files import copy, get
import os


class CrashCatchConan(ConanFile):
    name = "crashcatch"
    description = "A cross-platform, single-header C++ crash-reporting library for modern C++ applications."
    license = "MIT"
    author = "Keith Pottratz"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/keithpotz/CrashCatch"
    topics = ("crash-reporting", "crash-handler", "minidump", "header-only", "single-header")
    package_type = "header-library"
    no_copy_source = True

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True)

    def package_id(self):
        # Header-only: binary is the same regardless of compiler/settings
        self.info.clear()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        # No compiled lib — only headers
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        os_name = self.settings.get_safe("os")
        if os_name == "Windows":
            self.cpp_info.system_libs = ["DbgHelp", "User32"]
        elif os_name == "Linux":
            # backtrace() and dladdr() live in libdl on some distros
            self.cpp_info.system_libs = ["dl"]