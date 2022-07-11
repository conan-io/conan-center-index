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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    build_requires = (
        "libtool/2.4.6",
    )

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("Only Linux/FreeBSD/Macos supported")

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
                if self.settings.os == "Macos":
                    if self.settings.arch == "x86":
                        extra_args.append('--build=i686-apple-darwin11')
                    elif self.settings.arch == "x86_64":
                        extra_args.append('--build=x86_64-apple-darwin11')
                    else:
                        extra_args.append('--build=armv8-apple-darwin11')
                env_build.configure("../", args=extra_args, build=False, host=False, target=False)
                env_build.make()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", excludes=("*_build/*", "*doc/*", "*tests/*"), src="{}/src".format(self._source_subfolder), dst="include/", keep_path=True)
        self.copy("*.h", excludes=("*_build/*", "*doc/*", "*tests/*"), src="{}/include".format(self._source_subfolder), dst="include/", keep_path=True)
        self.copy("*.h", src="{}/_build/include/urcu/".format(self._source_subfolder), dst="include/urcu", keep_path=False)
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so*", dst="lib", keep_path=False)
            self.copy("*.dylib", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["urcu", "urcu-common"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
