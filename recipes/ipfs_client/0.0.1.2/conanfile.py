from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import sys
from os.path import dirname, join, realpath

required_conan_version = ">=1.64"

class IpfsChromium(ConanFile):
    name = "ipfs_client"
    description = "Library for acting as a trustless client of IFPS gateway(s). see: https://specs.ipfs.tech/http-gateways/trustless-gateway/"
    homepage = "https://github.com/little-bear-labs/ipfs-chromium/tree/main/library"
    topics = ("ipfs", "ipns", "dweb", "web", "content-addressed", "network", "client", "io", "api", "file-sharing", "gateway", "kubo")
    license = "MIT,Apache-2.0,https://raw.githubusercontent.com/little-bear-labs/ipfs-chromium/main/library/LICENSE"
    url = 'https://github.com/conan-io/conan-center-index'
    settings = [ "os", "compiler", "build_type", "arch" ]
    _PB = 'protobuf/3.20.0'
    require_transitively = [
        'abseil/20230125.3',
        'boost/1.81.0',
        'bzip2/1.0.8',
        'c-ares/1.22.1',
        'nlohmann_json/3.11.2',
        'openssl/1.1.1w',
        _PB,
    ]
    default_options = {"boost/*:bzip2": True}
    tool_requires = [
        'cmake/3.22.6',
        'ninja/1.11.1',
        _PB,
    ]
    extensions = ['h', 'cc', 'hpp', 'proto']
    exports_sources = [ '*.txt' ] + [f'**/*.{e}' for e in extensions]
    exports = 'version.txt'
    package_type = 'static-library'

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self, 'Ninja')
        tc.generate()
        d = CMakeDeps(self)
        d.generate()

    def build(self):
        cmake = CMake(self)
        if self.settings.compiler.cppstd:
          stdver = self.settings.compiler.cppstd
        else:
          stdver = 20
        cmake.configure(variables={
            "CXX_VERSION": stdver,
            "INSIDE_CONAN": True
        })
        cmake.build(build_tool_args=['--verbose'])

    def package(self):
        s = join(self.source_folder, 'library')
        d = join(self.package_folder, "licenses")
        copy(self, pattern="LICENSE*", dst=d, src=s)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ipfs_client", "ic_proto"]

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        for l in self.require_transitively:
            self.requires(l, transitive_headers=True)

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "14",
            "gcc": "11",
            "msvc": "193"
        }

    def validate(self):
        cc_nm = str(self.settings.compiler)
        if cc_nm not in [ "gcc", "apple-clang"]:
            raise ConanInvalidConfiguration(f"TODO: support for {cc_nm} not in this release")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)
        minimum_version = self._minimum_compilers_version.get(cc_nm, False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} does not support your compiler.")
