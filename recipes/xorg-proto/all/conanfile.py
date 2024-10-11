from conan import ConanFile
from conan.tools.files import rmdir, mkdir, save, load, get, apply_conandata_patches, export_conandata_patches, copy
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

import glob
import os
import re
import yaml

required_conan_version = ">=1.54.0"


class XorgProtoConan(ConanFile):
    name = "xorg-proto"
    package_type = "header-library"
    description = "This package provides the headers and specification documents defining " \
        "the core protocol and (many) extensions for the X Window System."
    topics = ("specification", "x-window")
    license = "X11"
    homepage = "https://gitlab.freedesktop.org/xorg/proto/xorgproto"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "PkgConfigDeps"

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires("automake/1.16.5")
        self.tool_requires("xorg-macros/1.19.3")
        self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def requirements(self):
        if hasattr(self, "settings_build"):
            self.requires("xorg-macros/1.19.3")

    def package_id(self):
        self.info.clear()

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper"))
            env.define("CC", f"{compile_wrapper} cl -nologo")
        tc.generate(env)

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _pc_data_path(self):
        return os.path.join(self.package_folder, "res", "pc_data.yml")

    def package(self):
        copy(self, "COPYING-*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        pc_data = {}
        for fn in glob.glob(os.path.join(self.package_folder, "share", "pkgconfig", "*.pc")):
            pc_text = load(self, fn)
            filename = os.path.basename(fn)[:-3]
            name = next(re.finditer("^Name: ([^\n$]+)[$\n]", pc_text, flags=re.MULTILINE)).group(1)
            version = next(re.finditer("^Version: ([^\n$]+)[$\n]", pc_text, flags=re.MULTILINE)).group(1)
            pc_data[filename] = {
                "version": version,
                "name": name,
            }
        mkdir(self, os.path.dirname(self._pc_data_path))
        save(self, self._pc_data_path, yaml.dump(pc_data))

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        for filename, name_version in yaml.safe_load(open(self._pc_data_path)).items():
            self.cpp_info.components[filename].filenames["pkg_config"] = filename
            self.cpp_info.components[filename].libdirs = []
            if hasattr(self, "settings_build"):
                self.cpp_info.components[filename].requires = ["xorg-macros::xorg-macros"]
            self.cpp_info.components[filename].version = name_version["version"]
            self.cpp_info.components[filename].set_property("pkg_config_name", filename)

        self.cpp_info.components["xproto"].includedirs.append(os.path.join("include", "X11"))
