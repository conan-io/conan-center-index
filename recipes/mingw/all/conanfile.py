import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class MingwConan(ConanFile):
    name = "mingw"
    description = "MinGW is a contraction of Minimalist GNU for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mingw.org"
    license = "ZPL-2.1", "MIT", "GPL-2.0-or-later"
    topics = ("gcc", "gnu", "unix", "mingw32", "binutils")
    settings = "os", "arch", "compiler"
    build_requires = "7zip/19.00"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("MinGW is only supported by Windows.")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("MinGW is only supports gcc.")

    def _get_best_installer(self):
        host_arch = str(self.settings.arch)
        compiler_version = str(self.settings.compiler.version)
        compiler_exception = str(self.settings.compiler.exception)
        compiler_threads = str(self.settings.compiler.threads)
        return self.conan_data["sources"][self.version]["url"][compiler_version][host_arch][compiler_threads][compiler_exception]

    def build(self):
        url = self._get_best_installer()
        self.output.info("Downloading: %s" % url["url"])
        tools.download(url["url"], "file.7z", sha256=url["sha256"])
        self.run("7z x file.7z")
        os.remove('file.7z')

    def package(self):
        target = "mingw64" if self.settings.arch == "x86_64" else "mingw32"
        self.copy("*", dst="", src=target)
        tools.rmdir(target)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.env_info.MINGW_HOME = str(self.package_folder)
        self.env_info.CONAN_CMAKE_GENERATOR = "MinGW Makefiles"
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/")
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/")
