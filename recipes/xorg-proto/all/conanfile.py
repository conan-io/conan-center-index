from conans import AutoToolsBuildEnvironment, ConanFile, tools
import glob
import os
import re
import yaml

required_conan_version = ">=1.33.0"


class XorgProtoConan(ConanFile):
    name = "xorg-proto"
    description = "This package provides the headers and specification documents defining " \
        "the core protocol and (many) extensions for the X Window System."
    topics = ("conan", "xproto", "header", "specification")
    license = "X11"
    homepage = "https://gitlab.freedesktop.org/xorg/proto/xorgproto"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_autotools()
        autotools.make()

    @property
    def _pc_data_path(self):
        return os.path.join(self.package_folder, "res", "pc_data.yml")

    def package(self):
        self.copy("COPYING-*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        pc_data = {}
        for fn in glob.glob(os.path.join(self.package_folder, "share", "pkgconfig", "*.pc")):
            pc_text = tools.load(fn)
            filename = os.path.basename(fn)[:-3]
            name = next(re.finditer("^Name: ([^\n$]+)[$\n]", pc_text, flags=re.MULTILINE)).group(1)
            version = next(re.finditer("^Version: ([^\n$]+)[$\n]", pc_text, flags=re.MULTILINE)).group(1)
            pc_data[filename] = {
                "version": version,
                "name": name,
            }
        tools.mkdir(os.path.dirname(self._pc_data_path))
        tools.save(self._pc_data_path, yaml.dump(pc_data))

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        for filename, name_version in yaml.safe_load(open(self._pc_data_path)).items():
            # FIXME: generated .pc files contain `Name: xorg-proto-Xproto`, it should be `Name: Xproto`
            self.cpp_info.components[filename].libdirs = []
            self.cpp_info.components[filename].version = name_version["version"]

        self.cpp_info.components["xproto"].includedirs.append(os.path.join("include", "X11"))
