from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, load, save, download
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
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("No binaries available for the architecture '{}'.".format(self.settings.arch))
        if str(self.settings.os) not in ("Windows", "Linux", "Macos"):
            raise ConanInvalidConfiguration("No binaries available for the OS '{}'.".format(self.settings.os))

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("7zip/19.00")

    def build(self):
        if self.settings.os == "Windows":
            filename =  os.path.join(self.build_folder, "GCC-10.2.0-crt-8.0.0-with-ada-20201019.7z")
            download(self, **self.conan_data["sources"][self.version][str(self.settings.os)]["x86_64"], filename=filename)
            self.run(f"7z x {filename}")
        else:
            get(self, **self.conan_data["sources"][self.version][str(self.settings.os)]["x86_64"],
                    destination=self.build_folder, strip_root=True)

    @property
    def _archive_contents_path(self):
        if self.settings.os == "Macos":
            return os.path.join(self.build_folder, "local")
        elif self.settings.os == "Windows":
            return os.path.join(self.build_folder, "mingw64")
        else:
            return os.path.join(self.build_folder)

    @property
    def _license_path(self):
        return os.path.join(self._archive_contents_path, "share", "info")

    @property
    def _library_source_path(self):
        return os.path.join(self._archive_contents_path, {
            "Linux":  "lib64",
            "Macos": "lib",
            "Windows": os.path.join("lib", "gcc", "x86_64-w64-mingw32", "10.2.0")
        }[str(self.settings.os)])

    def _extract_license(self):
        info = load(self, os.path.join(self._license_path, "gfortran.info"))
        license_contents = info[info.find("Version 3"):info.find("END OF TERMS", 1)]
        save(self, os.path.join(self.build_folder, "LICENSE"), license_contents)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type # The binaries are not specific

    def package(self):
        self._extract_license()
        copy(self, "LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "gfortran*", src=os.path.join(self._archive_contents_path, "bin"), dst=os.path.join(self.package_folder, "bin"))
        copy(self, "libgfortran.a", src=self._library_source_path, dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.cpp_info.includedirs = []
        self.env_info.PATH.append(bin_path)
        self.cpp_info.libs = ["gfortran"]
