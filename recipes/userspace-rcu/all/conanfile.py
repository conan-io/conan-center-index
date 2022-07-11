from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class UserspaceRCUConan(ConanFile):
    name = "userspace-rcu"
    homepage ="https://liburcu.org/"
    description = "Userspace RCU (read-copy-update) library"
    topics = ("conan", "urcu")
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPLv2.1"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "model": ["generic", "mb", "signal", "bp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "model": "generic",
    }
    build_requires = (
        "libtool/2.4.6",
    )

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Only Linux/FreeBSD supported")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("./bootstrap")
            tools.mkdir("_build")
            with tools.chdir("_build"):
                env_build = AutoToolsBuildEnvironment(self)
                extra_args = list()
                if self.options.shared:
                    extra_args.append('--enable-static=no')
                else:
                    extra_args.append('--enable-shared=no')
                env_build.configure("../", args=extra_args, build=False, host=False, target=False)
                env_build.make()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", excludes=("*_build/*", "*doc/*", "*tests/*"), src="{}/src".format(self._source_subfolder), dst="include/", keep_path=True)
        self.copy("*.h", excludes=("*_build/*", "*doc/*", "*tests/*"), src="{}/include".format(self._source_subfolder), dst="include/", keep_path=True)
        self.copy("*.h", src="{}/_build/include/urcu/".format(self._source_subfolder), dst="include/urcu", keep_path=False)
        lib_name = ''
        if self.options.model == "generic":
            lib_name = 'liburcu'
        elif self.options.model == "mb":
            lib_name = 'liburcu-mb'
        elif self.options.model == "signal":
            lib_name = 'liburcu-signal'
        else:
            lib_name = 'liburcu-bp'
        if self.options.shared:
            self.copy("*{}.dll".format(lib_name), dst="bin", keep_path=False)
            self.copy("*{}.so*".format(lib_name), dst="lib", keep_path=False)
            self.copy("*{}.dylib".format(lib_name), dst="lib", keep_path=False)
        else:
            self.copy("*{}.a".format(lib_name), dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.model == "mb":
            self.cpp_info.cxxflags = ["-DRCU_MB"]
        elif self.options.model == "signal":
            self.cpp_info.cxxflags = ["-DRCU_SIGNAL"]
        elif self.options.model == "bp":
            self.cpp_info.cxxflags = ["-DRCU_BP"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
