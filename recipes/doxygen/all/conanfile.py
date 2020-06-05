from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class DoxygenInstallerConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("conan", "doxygen", "installer", "devtool", "documentation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"

    settings = "os", "arch",

    def config(self):
        if self.settings.os in ["Linux", "Macos"] and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("Doxygen is not supported on {}-{}".format(self.os, self.arch))

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
            "Windows": "windows.bin" if self.settings.arch == "x86" else "windows.x64.bin",
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
            if os_name[str(self.settings.os)] in url:
                dest_file = filename

        if not dest_file:
            raise ConanInvalidConfiguration("could not find source file fo the configuration")

        tools.unzip("doxygen-{}.linux.bin.tar.gz".format(self.version), pattern="*LICENSE")

        if self.settings.os == "Macos":
            self.unpack_dmg(dest_file)
            # Redirect the path of libclang.dylib to be adjacent to the doxygen executable, instead of in Frameworks
            self.run('install_name_tool -change "@executable_path/../Frameworks/libclang.dylib" "@executable_path/libclang.dylib" doxygen')
        else:
            tools.unzip(dest_file)

    def package(self):
        if self.settings.os == "Linux":
            srcdir = "doxygen-{}/bin".format(self.version)
            self.copy("*", dst="bin", src=srcdir)

        self.copy("doxygen", dst="bin")
        self.copy("doxyindexer", dst="bin")
        self.copy("doxysearch.cgi", dst="bin")
        self.copy("*.exe", dst="bin")
        self.copy("*.dylib", dst="bin")
        self.copy("*.dll", dst="bin")
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
