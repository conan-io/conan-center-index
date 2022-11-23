from conan import ConanFile, tools
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, collect_libs, get
from conans import AutoToolsBuildEnvironment


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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        buildenv = AutoToolsBuildEnvironment(self)
        buildenv.flags = ["-std=gnu99", "-pedantic"]
        if not self.options.shared:
            buildenv.fpic = self.options.fPIC
            buildenv.make(target="alib")
        elif is_apple_os(self):
            buildenv.make(target="dylib")
        else:
            buildenv.make(target="solib")

    def package(self):
        self.copy("LICENSE", dst="licenses", keep_path=False)
        self.copy("*.h", dst="include", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
