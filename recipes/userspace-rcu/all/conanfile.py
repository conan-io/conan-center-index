import os

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.tools.files import get, rmdir
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47.0"


class UserspaceRCUConan(ConanFile):
    name = "userspace-rcu"
    homepage ="https://liburcu.org/"
    description = "Userspace RCU (read-copy-update) library"
    topics = ("urcu")
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    build_requires = (
        "libtool/2.4.6",
    )

    generators = "PkgConfigDeps"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("Building for {} unsupported".format(self.settings.os))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools


    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            self.run("./bootstrap")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        for lib_type in ["", "-bp", "-cds", "-mb", "-memb", "-qsbr", "-signal"]:
            component_name = "urcu{}".format(lib_type)
            self.cpp_info.components[component_name].libs = ["urcu-common", component_name]
            self.cpp_info.components[component_name].set_property("pkg_config_name", component_name)
            self.cpp_info.components[component_name].names["pkg_config"] = component_name
            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components[component_name].includedirs = ["include"]
            self.cpp_info.components[component_name].libdirs = ["lib"]
            if self.settings.os == "Linux":
                self.cpp_info.components[component_name].system_libs = ["pthread"]

        # Some definitions needed for MB and Signal variants
        self.cpp_info.components["urcu-mb"].defines = ["RCU_MB"]
        self.cpp_info.components["urcu-signal"].defines = ["RCU_SIGNAL"]
