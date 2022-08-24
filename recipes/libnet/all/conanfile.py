from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibnetConan(ConanFile):
    name = "libnet"

    description = "Libnet is an API to help with the construction and injection of network packets."
    topics = ("conan", "libnet", "network")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libnet.sourceforge.net/"
    license = ["BSD-2-Clause"]
    settings = "os", "arch", "compiler", "build_type"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libnet is not supported by Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("libnet can't be built as shared on Windows")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)

        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
            args.append("--disable-doxygen-doc")

        self._autotools.configure(configure_dir=self._source_subfolder, args=args)

        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        os.unlink(os.path.join(self.package_folder, "lib", "libnet.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "pkgconfig", "libnet.pc"))

    def package_info(self):
        self.cpp_info.libs = ["net"]
        self.cpp_info.names["pkg_config"] = "libnet"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
