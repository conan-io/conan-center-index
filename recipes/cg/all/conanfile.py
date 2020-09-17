import os
import glob
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class CgConan(ConanFile):
    name = "cg"
    description = "The Nvidia Cg Toolkit provides a compiler for the Cg language, runtime libraries for use with " \
                  "both leading graphics APIs, runtime libraries for CgFX, example applications, and extensive " \
                  "documentation."
    homepage = "https://developer.nvidia.com/cg-toolkit"
    topics = ("conan", "cg", "shading")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch"
    license = "License For Customer Use of NVIDIA Software"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os not in ["Windows", "Linux", "Macos"]:
            raise ConanInvalidConfiguration("cg doesn't support OS: {}.".format(self.settings.os))
        if self.settings.arch not in ["x86_64", "x86"]:
            raise ConanInvalidConfiguration("cg doesn't support arch: {}".format(self.settings.arch))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("Cg-Toolkit-*".format(self.version))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        arch_str = str(self.settings.arch)

        if self.settings.os == "Windows":
            self.copy("*.h", dst=os.path.join("include", "Cg"), src=os.path.join(self._source_subfolder, "win", "include", "Cg"))
            self.copy("cg*", dst="bin", src=os.path.join(self._source_subfolder, "win", "bin", arch_str), keep_path=False)
            self.copy("cg*.lib", dst="lib", src=os.path.join(self._source_subfolder, "win", "lib", arch_str), keep_path=False)

        elif self.settings.os == "Linux":
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "linux", "include"))
            self.copy("*", dst="bin", src=os.path.join(self._source_subfolder, "linux", "bin", arch_str), keep_path=False)
            self.copy("*.so*", dst="lib", src=os.path.join(self._source_subfolder, "linux", "lib", arch_str), keep_path=False)

        elif self.settings.os == "Macos":
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "mac", "include"))
            self.copy("*", dst="bin", src=os.path.join(self._source_subfolder, "mac", "bin"), keep_path=False)
            self.copy("*.dylib", dst="lib", src=os.path.join(self._source_subfolder, "mac", "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
