from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


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
            tools.rename("mingw64", self._source_subfolder)
        else:
            tools.get(**sources, strip_root=True, destination =self._source_subfolder)

    def _extract_license(self):
        info = tools.load(os.path.join(self.source_folder, self._source_subfolder, "share", "info", "gfortran.info"))
        license_contents = info[info.find("Version 3"):info.find("END OF TERMS", 1)]
        tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        self.copy("gfortran*", dst="bin", src=os.path.join(self._source_subfolder, "bin"))
        self.copy("gfortran", dst="bin", src=os.path.join(self._source_subfolder, "local", "bin"))
        self.copy("libgfortran.a", dst="lib", src=os.path.join(self._source_subfolder, "lib64"))
        self.copy("libgfortran.a", dst="lib", src=os.path.join(self._source_subfolder, "local", "lib"))
        self.copy("libgfortran.a", dst="lib", src=os.path.join(self._source_subfolder, "lib", "gcc", "x86_64-w64-mingw32", "10.2.0"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.libs = ["gfortran"]
