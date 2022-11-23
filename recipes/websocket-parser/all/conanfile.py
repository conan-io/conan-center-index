from conan import ConanFile
from conans.client.build.autotools_environment import AutoToolsBuildEnvironment
from conan.tools.files import apply_conandata_patches, chdir, get

class WebsocketParserConan(ConanFile):
    name = "websocket-parser"
    license = "BSD-3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/php-ion/websocket-parser"
    description = "Streaming websocket frame parser and frame builder for c"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/**"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        buildenv = AutoToolsBuildEnvironment(self)
        buildenv.fpic = self.options.fPIC
        buildenv.flags = ["-std=gnu99", "-pedantic"]
        buildenv.make(target="solib" if self.options.shared else "alib")

    def package(self):
        self.copy("*.h", dst="include", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["libwebsocket_parser"]
