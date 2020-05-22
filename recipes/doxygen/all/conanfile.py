from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class DoxygenInstallerConan(ConanFile):
    name = "doxygen"
    version = "1.8.17"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("conan", "doxygen", "installer", "devtool", "documentation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/doxygen/doxygen"
    author = "Inexor <info@inexor.org>"
    license = "GPL-2.0-only"

    settings = {
        "os_build": ["Windows", "Linux", "Macos"],
        "arch_build": ["x86", "x86_64"]
    }
#   options = {"build_from_source": [False, True]} NOT SUPPORTED YET
#   default_options = "build_from_source=False"

    def config(self):
        if self.settings.os_build in ["Linux", "Macos"] and self.settings.arch_build == "x86":
            raise ConanInvalidConfiguration("x86 is not supported on Linux or Macos")

    def unpack_dmg(self, dest_file):
        mount_point = os.path.join(self.build_folder, "mnt")
        tools.mkdir(mount_point)
        self.run("hdiutil attach -mountpoint %s %s" % (mount_point, dest_file))
        try:
            for program in ["doxygen", "doxyindexer", "doxysearch.cgi"]:
                shutil.copy(os.path.join(mount_point, "Doxygen.app", "Contents",
                                         "Resources", program), self.build_folder)
            shutil.copy(os.path.join(mount_point, "Doxygen.app", "Contents",
                                    "Frameworks", "libclang.dylib"), self.build_folder)
        finally:
            self.run("diskutil eject %s" % (mount_point))
            tools.rmdir(mount_point)

    def build(self):
        os_name = {
            "Windows": "windows.bin" if self.settings.arch_build == "x86" else "windows.x64.bin",
            "Macos": ".dmg",
            "Linux": "linux"
        }
        dest_file = None
        for data in self.conan_data["sources"][self.version]:
            sha = data["sha256"]
            url = data["url"]
            filename = url[url.rfind("/") + 1:]
            self.output.info("Downloading: {}".format(url))
            tools.download(url, filename)
            tools.check_sha256(filename, sha)
            if os_name[str(self.settings.os_build)] in url:
                dest_file = filename

        if not dest_file:
            raise ConanInvalidConfiguration("could not find source file fo the configuration")

        if self.settings.os_build == "Macos":
            self.unpack_dmg(dest_file)
            # Redirect the path of libclang.dylib to be adjacent to the doxygen executable, instead of in Frameworks
            self.run('install_name_tool -change "@executable_path/../Frameworks/libclang.dylib" "@executable_path/libclang.dylib" doxygen')
        else:
            tools.unzip(dest_file)

    def package(self):
        if self.settings.os_build == "Linux":
            srcdir = "doxygen-{}/bin".format(self.version)
            self.copy("*", dst="bin", src=srcdir)

        self.copy("doxygen", dst="bin")
        self.copy("doxyindexer", dst="bin")
        self.copy("doxysearch.cgi", dst="bin")
        self.copy("*.exe", dst="bin")
        self.copy("*.dylib", dst="bin")
        self.copy("*.dll", dst="bin")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
