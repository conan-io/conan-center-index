from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy, get, load, save, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class GnuConfigConan(ConanFile):
    name = "gnu-config"
    description = "The GNU config.guess and config.sub scripts"
    homepage = "https://savannah.gnu.org/projects/config/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("gnu", "config", "autotools", "canonical", "host", "build", "target", "triplet")
    license = "GPL-3.0-or-later", "autoconf-special-exception"
    os = "arch", "compiler", "build_type", "arch"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def _extract_license(self):
        txt_lines = load(self, os.path.join(self.source_folder, "config.guess")).splitlines()
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
        save(self, os.path.join(self.package_folder, "licenses", "COPYING"), self._extract_license())
        copy(self, "config.guess", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        copy(self, "config.sub", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.conf_info.define("user.gnu-config:config_guess", os.path.join(bin_path, "config.guess"))
        self.conf_info.define("user.gnu-config:config_sub", os.path.join(bin_path, "config.sub"))

        # TODO: to remove in conan v2
        self.user_info.CONFIG_GUESS = os.path.join(bin_path, "config.guess")
        self.user_info.CONFIG_SUB = os.path.join(bin_path, "config.sub")
        self.env_info.PATH.append(bin_path)
