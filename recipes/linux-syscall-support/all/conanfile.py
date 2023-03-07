import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, save


class LinuxSyscallSupportConan(ConanFile):
    name = "linux-syscall-support"
    description = "Linux Syscall Support provides a header file that can be included into your application whenever you need to make direct system calls."
    homepage = "https://chromium.googlesource.com/linux-syscall-support"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "linux", "syscall", "chromium")
    license = "BSD-3-Clause"
    settings = "os"
    no_copy_source = True

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} supported only on Linux".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, pattern="linux_syscall_support.h", src=self.source_folder, dst="include")
        with open(os.path.join(self.source_folder, "linux_syscall_support.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(0, 29):
            license_content.append(content_lines[i][3:-1])
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"),
             "\n".join(license_content))
