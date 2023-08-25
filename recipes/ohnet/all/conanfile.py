from conan import ConanFile
from conan.tools.files import get, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain


required_conan_version = ">=1.53.0"


class OhNetConan(ConanFile):
    name = "ohnet"
    description = "OpenHome Networking (ohNet) is a modern, cross platform, multi-language UPnP stack"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openhome/ohNet"
    topics = ("openhome", "ohnet", "upnp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args.append("-j1")
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="ohNetDll TestsNative proxies devices")
