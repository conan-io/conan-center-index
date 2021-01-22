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
    options = {"threads": ["posix", "win32"], "exception": ["seh", "sjlj"]}
    default_options = {"threads": "posix", "exception": "seh"}
    build_requires = "7zip/19.00"
    no_copy_source = True

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("MinGW is only supported by Windows.")
        if self.settings.compiler == "gcc":
            if str(self.settings.compiler.threads) != str(self.options.threads):
                self.output.warn("MinGW threads may not differ from 'settings.compiler.threads'.")
            if str(self.settings.compiler.exception) != str(self.options.exception):
                self.output.warn("MinGW exception may not differ from 'settings.compiler.exception'.")
        else:
            self.output.warn("Only 'gcc' should be used as compiler.")

    def source(self):
        url = self.conan_data["sources"][self.version]["url"][str(self.settings.arch)] \
                             [str(self.options.threads)][str(self.options.exception)]
        self.output.info("Downloading: %s" % url["url"])
        tools.download(url["url"], "file.7z", sha256=url["sha256"])
        self.run("7z x file.7z")
        os.remove('file.7z')

    def package(self):
        target = "mingw64" if self.settings.arch == "x86_64" else "mingw32"
        self.copy("*", dst="", src=target)
        tools.rmdir(target)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.env_info.MINGW_HOME = str(self.package_folder)
        self.env_info.CONAN_CMAKE_GENERATOR = "MinGW Makefiles"
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/")
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/")
