from conans import tools, ConanFile, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class IntelIpSecMbConan(ConanFile):
    name = "intel-ipsec-mb"
    description = "Intel(R) Multi-Buffer Crypto for IPSec"
    license = "BSD-3-Clause"
    homepage = "https://github.com/intel/intel-ipsec-mb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("intel", "IPSec", "IPSec_MB")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("nasm/2.15.05")

    def validate(self):
        if self.settings.arch != "x86_64":
            message = "{} is not supported".format(self.settings.arch)
            raise ConanInvalidConfiguration(message)
        if self.settings.os not in ("FreeBSD", "Linux", "Windows"):
            message = "{} is not supported".format(self.settings.os)
            raise ConanInvalidConfiguration(message)
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("intel-ipsec-mb only supports Visual Studio on Windows")

    def build(self):
        yn = lambda v: "y" if v else "n"
        make_args = [
            "SHARED={}".format(yn(self.options.shared)),
            "DEBUG={}".format(yn(self.settings.build_type == "Debug")),
        ]
        with tools.chdir(os.path.join(self._source_subfolder, "lib")):
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file("win_x64.mak",
                                      "-MD", "-{}".format(self.settings.compiler.runtime))
                with tools.vcvars(self):
                    self.run("nmake -nologo -fwin_x64.mak {}".format(" ".join(arg for arg in make_args)))
            else:
                autotools = self._configure_autotools()
                autotools.make(args=make_args)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("intel-ipsec-mb.h", src=os.path.join(self._source_subfolder, "lib"), dst="include", keep_path=False)
        self.copy("*.lib", src=self._source_subfolder, dst="lib", keep_path=False)
        self.copy("*.so*", src=self._source_subfolder, dst="lib", keep_path=False)
        self.copy("*.a", src=self._source_subfolder, dst="lib", keep_path=False)
        self.copy("*.dll", src=self._source_subfolder, dst="bin", keep_path=False)
        if self.settings.compiler == "Visual Studio":
            tools.rename(os.path.join(self.package_folder, "lib", "libIPSec_MB.lib"),
                         os.path.join(self.package_folder, "lib", "IPSec_MB.lib"))

    def package_info(self):
        self.cpp_info.libs = ["IPSec_MB"]
