from conans import ConanFile, tools
import os
import shutil

required_conan_version = ">=1.33.0"


class GnuLibConanFile(ConanFile):
    name = "gnulib"
    description = "Gnulib is a central location for common GNU code, intended to be shared among GNU packages."
    homepage =  "https://www.gnu.org/software/gnulib/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("gnulib", "library", "gnu")
    license = ("GPL-3.0-or-later", "LGPL-3.0-or-later", "Unlicense")

    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True, filename="gnulib.tar.gz")

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        # The following line did not work, so do it the long way...
        # shutil.copy(os.path.join(self.source_folder, self._source_subfolder), os.path.join(self.package_folder, "bin"))

        gnulib_dir = os.path.join(self.source_folder, self._source_subfolder)
        for root, _, files in os.walk(gnulib_dir):
            relpath = os.path.relpath(root, gnulib_dir)
            dstdir = os.path.join(self.package_folder, "bin", relpath)
            try:
                os.makedirs(dstdir)
            except FileExistsError:
                pass
            for file in files:
                src = os.path.join(root, file)
                dst = os.path.join(dstdir, file)
                shutil.copy(src, dst)

    def package_info(self):
        self.cpp_info.libdirs = []

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(binpath))
        self.env_info.PATH.append(binpath)
