from conan import ConanFile
from conan.tools.files import rmdir, mkdir, save, load
from conans import AutoToolsBuildEnvironment, tools
import contextlib
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
    settings = "os", "arch", "compiler", "build_type"

    generators = "PkgConfigDeps"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build_requirements(self):
        self.build_requires("automake/1.16.3")
        self.build_requires("xorg-macros/1.19.3")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        if hasattr(self, "settings_build"):
            self.requires("xorg-macros/1.19.3")

    def package_id(self):
        # self.info.header_only() would be fine too, but keep the os to add c3i test coverage for Windows.
        del self.info.settings.arch
        del self.info.settings.build_type
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} cl -nologo".format(self._user_info_build["automake"].compile).replace("\\", "/"),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _pc_data_path(self):
        return os.path.join(self.package_folder, "res", "pc_data.yml")

    def package(self):
        self.copy("COPYING-*", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
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
