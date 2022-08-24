from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
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
        return os.path.join(self.source_folder, "source_subfolder_{}".format(str(self.settings.os)))

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("No binaries available for the architecture '{}'.".format(self.settings.arch))
        if str(self.settings.os) not in ("Windows", "Linux", "Macos"):
            raise ConanInvalidConfiguration("No binaries available for the OS '{}'.".format(self.settings.os))

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("7zip/19.00")

    def source(self):
        url = self.conan_data["sources"][self.version]["url"]
        for it in url.keys():
            if self.settings.os == "Windows" and it == "Windows":
                filename = url[it]["filename"]
                tools.files.download(self, **url[it])
                self.run("7z x {0}".format(filename))
                os.unlink(filename)
                os.rename("mingw64", "source_subfolder_Windows")
            elif it != "Windows":
                tools.files.get(self, **url[it])
                pattern = "gcc-*" if it == "Linux" else "usr"
                os.rename(glob.glob(pattern)[0], "source_subfolder_{}".format(it))

    def _extract_license(self):
        info = tools.files.load(self, os.path.join(self.source_folder, "source_subfolder_Linux", "share", "info", "gfortran.info"))
        license_contents = info[info.find("Version 3"):info.find("END OF TERMS", 1)]
        tools.files.save(self, "LICENSE", license_contents)

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
