import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class LinuxSyscallSupportConan(ConanFile):
    name = "linux-syscall-support"
    description = "Linux Syscall Support provides a header file that can be included into your application whenever you need to make direct system calls."
    license = "BSD-3-Clause"
    topics = ("linux", "syscall", "chromium")
    homepage = "https://chromium.googlesource.com/linux-syscall-support"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "header-library"
    settings = "os"
    no_copy_source = True

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} supported only on Linux".format(self.name))

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def package_id(self):
        self.info.clear()

    def _extract_license(self):
        with open(os.path.join(self.source_folder, "linux_syscall_support.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(0, 29):
            license_content.append(content_lines[i][3:-1])
        return "\n".join(license_content)

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        copy(self, "linux_syscall_support.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
