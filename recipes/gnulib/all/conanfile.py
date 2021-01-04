from conans import ConanFile, tools
import os
import re
import shutil


class GnuLibConanFile(ConanFile):
    name = "gnulib"
    description = "Gnulib is a central location for common GNU code, intended to be shared among GNU packages."
    homepage =  "https://www.gnu.org/software/gnulib/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "gnulib", "library", "gnu")
    license = ("GPL-3.0-or-later", "LGPL-3.0-or-later", "Unlicense")
    no_copy_source = True

    # Added to test on CI
    settings = "os_build", "arch_build"

    _source_subfolder = "source_subfolder"

    def source(self):
        hash = re.search(r"h=([0-9a-f]*)", self.conan_data["sources"][self.version]["url"]).group(1)
        dirname = "{}-{}".format(self.name, hash[:7])
        tools.get(**self.conan_data["sources"][self.version], filename="gnulib-{}.tar.gz".format(dirname))
        os.rename(dirname, self._source_subfolder)

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

    def package_id(self):
        self.info.include_build_settings()

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(binpath))
        self.env_info.PATH.append(binpath)
