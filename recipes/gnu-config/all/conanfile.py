from conans import ConanFile, tools
from conans.errors import ConanException
import glob
import os


class GnuConfigConan(ConanFile):
    name = "gnu-config"
    description = "The GNU config.guess and config.sub scripts"
    homepage = "https://savannah.gnu.org/projects/config/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "gnu", "config", "autotools", "canonical", "host", "build", "target", "triplet")
    license = "GPL-3.0-or-later", "autoconf-special-exception"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("config*")[0], self._source_subfolder)

    def _extract_license(self):
        txt_lines = tools.load(os.path.join(self.source_folder, self._source_subfolder, "config.guess")).splitlines()
        start_index = None
        end_index = None
        for line_i, line in enumerate(txt_lines):
            if start_index is None:
                if "This file is free" in line:
                    start_index = line_i
            if end_index is None:
                if "Please send patches" in line:
                    end_index = line_i
        if not all((start_index, end_index)):
            raise ConanException("Failed to extract the license")
        return "\n".join(txt_lines[start_index:end_index])

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING"), self._extract_license())
        self.copy("config.guess", src=self._source_subfolder, dst="bin")
        self.copy("config.sub", src=self._source_subfolder, dst="bin")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        self.user_info.CONFIG_GUESS = os.path.join(bin_path, "config.guess")
        self.user_info.CONFIG_SUB = os.path.join(bin_path, "config.sub")
