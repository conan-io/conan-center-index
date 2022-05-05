from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.32.0"


class GFortranConan(ConanFile):
    name = "gfortran"
    description = "The Fortran compiler front end and run-time libraries for GCC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gcc.gnu.org/fortran"
    topics = ("gnu", "gcc", "fortran", "compiler")
    license = "GPL-3.0-or-later"
    settings = "os", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("No binaries available for the architecture '{}'.".format(self.settings.arch))
        if str(self.settings.os) not in ("Windows", "Linux", "Macos"):
            raise ConanInvalidConfiguration("No binaries available for the OS '{}'.".format(self.settings.os))

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("7zip/19.00")

    def source(self):
        sources = self.conan_data["sources"][self.version][str(self.settings.os)]
        if sources["url"].endswith(".7z"):
            filename = "archive.7z"
            tools.download(**sources, filename=filename)
            self.run("7z x {0}".format(filename))
            os.unlink(filename)
        else:
            # can't use strip_root on linux because if fails with:
            # KeyError: "linkname 'gcc-10.2.0/bin/g++' not found"
            tools.get(**sources, strip_root=(self.settings.os == "Macos"))
        root_folder = {
            "Linux": "gcc-%s" % self.version,
            "Macos": "local",
            "Windows": "mingw64"
        }
        tools.rename(root_folder[str(self.settings.os)], self._source_subfolder)

    def _extract_license(self):
        base_folder = "local" if self.settings.os == "Macos" else ""
        info = tools.load(os.path.join(self.source_folder, self._source_subfolder, base_folder, "share", "info", "gfortran.info"))
        license_contents = info[info.find("Version 3"):info.find("END OF TERMS", 1)]
        tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        self.copy("gfortran*", dst="bin", src=os.path.join(self._source_subfolder, "bin"))

        tripplet = {
            "Linux": "x86_64-pc-linux-gnu",
            "Windows": "x86_64-w64-mingw32",
            "Macos": "x86_64-apple-darwin19"
        }[str(self.settings.os)]

        self.copy("libgfortran.spec", dst="lib", src=os.path.join(self._source_subfolder, "lib"))
        self.copy("*", dst="lib", src=os.path.join(self._source_subfolder, "lib", "gcc", tripplet, self.version))

        self.copy("libgfortran.a", dst="lib", src=os.path.join(self._source_subfolder, "lib64"))
        self.copy("libgfortran.a", dst="lib", src=os.path.join(self._source_subfolder, "lib"))

        self.copy("liblto_plugin-0.dll", dst=os.path.join("libexec", "gcc", tripplet, self.version), src=os.path.join(self._source_subfolder, "libexec", "gcc", tripplet, self.version))

        self.copy("f951*", dst=os.path.join("libexec", "gcc", tripplet, self.version), src=os.path.join(self._source_subfolder, "libexec", "gcc", tripplet, self.version))
        self.copy("as.exe", dst="bin", src=os.path.join(self._source_subfolder, "bin"))
        self.copy("ld.exe", dst="bin", src=os.path.join(self._source_subfolder, "bin"))

        self.copy("*", dst=".", src=os.path.join(self._source_subfolder, tripplet))

        tools.remove_files_by_mask(self.package_folder, "*.la*")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.libs = ["gfortran"]
