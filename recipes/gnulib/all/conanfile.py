import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class GnuLibConanFile(ConanFile):
    name = "gnulib"
    description = ("Gnulib is a central location for common GNU code, "
                   "intended to be shared among GNU packages.")
    license = ("GPL-3.0-or-later", "LGPL-3.0-or-later", "Unlicense")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gnulib/"
    topics = ("library", "gnu")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if conan_version.major >= 2 and self.settings.os == "Windows":
            # Currently fails with 'configure: error: could not determine .../automake-1.16/ar-lib "lib -nologo" interface'.
            # https://github.com/conan-io/conan-center-index/pull/18602#issuecomment-1639763920
            raise ConanInvalidConfiguration("Windows is currently not supported by the gnulib recipe. Contributions are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, filename="gnulib.tar.gz")

    def package(self):
        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment var: {binpath}")
        self.env_info.PATH.append(binpath)
