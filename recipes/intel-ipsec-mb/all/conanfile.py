from conans import tools, ConanFile, AutoToolsBuildEnvironment

required_conan_version = ">=1.39.0"

class IntelIpSecMbConan(ConanFile):
    name = "intel-ipsec-mb"
    description = "Intel(R) Multi-Buffer Crypto for IPSec"
    license = "BSD 3-Clause"
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
        print(self.conan_data["sources"][self.version])
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

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
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_MAKE_PROGRAM"):
            self.build_requires("make/4.2.1")
        self.build_requires("nasm/2.15.05")

    def validate(self):
        if self.settings.arch != "x86_64":
            message = "{} is not supported".format(self.settings.arch)
            raise ConanInvalidConfiguration(message)

    def build(self):
        autotools = self._configure_autotools()
        yn = lambda v: "y" if v else "n"
        args = [
            "SHARED={}".format(yn(self.options.shared)),
            "DEBUG={}".format(yn(self.settings.build_type == "Debug")),
        ]
        with tools.chdir(self._source_subfolder):
            autotools.make(args)

    def package(self):
        self.copy("*intel-ipsec-mb.h", "include",
                  self._source_subfolder, keep_path=False)
        self.copy("*.lib", "lib", self._source_subfolder, keep_path=False)
        self.copy("*.so*", "lib", self._source_subfolder, keep_path=False)
        self.copy("*.a", "lib", self._source_subfolder, keep_path=False)
        self.copy("*.dll", "bin", self._source_subfolder, keep_path=False)
        self.copy("LICENSE", "licenses", self._source_subfolder, keep_path=True)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "IPSec_MB"
        self.cpp_info.names["cmake_find_package_multi"] = "IPSec_MB"
        self.cpp_info.libs = ["IPSec_MB"]
