import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


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
        tools.get(**self.conan_data["sources"][self.version])

    def package_id(self):
        self.info.header_only()

    def _extract_license(self):
        with open(os.path.join(self.source_folder, "linux_syscall_support.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(0, 29):
            license_content.append(content_lines[i][3:-1])
        tools.save("LICENSE", "\n".join(license_content))

    def package(self):
        self.copy(pattern="linux_syscall_support.h", dst="include")
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses", keep_path=False)
