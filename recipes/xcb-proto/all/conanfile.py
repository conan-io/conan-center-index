from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import sys

class XCBProtoConan(ConanFile):
    name = "xcb-proto"
    description = "xcb-proto provides the XML-XCB protocol descriptions that libxcb uses to generate the majority of its code and API."
    topics = "x11", "xcb"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xcb.freedesktop.org/"
    license = "???"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        self.build_requires("automake/1.16.4")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configre_autotools(self):
        if self._autotools is not None:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_files(self):
        align_path = os.path.join(self._source_subfolder, "xcbgen", "align.py")
        tools.replace_in_file(align_path,
            "from fractions import gcd",
            "try:\n    from fractions import gcd\nexcept ImportError:\n    from math import gcd")

    def build(self):
        self._patch_files()        
        env_build = self._configre_autotools()
        env_build.make()

    def package(self):
        self.copy(pattern="*.xml", dst=os.path.join("share", "xcb"), src=os.path.join(self._source_subfolder, "src"))
        self.copy(pattern="*.xsd", dst=os.path.join("share", "xcb"), src=os.path.join(self._source_subfolder, "src"))
        env_build = self._configre_autotools()
        env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.rename(os.path.join(self.package_folder, "lib", "python%d.%d" % sys.version_info[:2]),
                  os.path.join(self.package_folder, "lib", "python%d" % sys.version_info[:1]))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "xcb-proto"

        xcbincludedir = os.path.join(self.package_folder, "share", "xcb")
        pythondir = os.path.join(self.package_folder, "lib", "python%d" % sys.version_info[:1], "site-packages")

        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "xcbincludedir={}\npythondir={}".format(xcbincludedir, pythondir))
        