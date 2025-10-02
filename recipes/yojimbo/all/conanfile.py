import os
from conan import ConanFile
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.premake import Premake, PremakeDeps, PremakeToolchain


required_conan_version = ">=2.19.0"


class YojimboConan(ConanFile):
    name = "yojimbo"
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/networkprotocol/yojimbo"
    topics = ("conan", "yojimbo", "game", "udp", "protocol", "client-server", "multiplayer-game-server")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libsodium/1.0.20")

    def build_requirements(self):
        self.tool_requires("premake/[>=5 <6, include_prerelease]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Remove hardcoded targetdir
        replace_in_file(self, os.path.join(self.source_folder, "premake5.lua"), 'targetdir "bin/"', "")
        # Disable warning as errors
        replace_in_file(self, os.path.join(self.source_folder, "premake5.lua"), 'flags { "FatalWarnings" }', "")

    def generate(self):
        deps = PremakeDeps(self)
        deps.generate()
        toolchain = PremakeToolchain(self)
        toolchain.generate()

    def build(self):
        premake = Premake(self)
        premake.configure()
        # Only build static libraries excluding tests projects and repackaged libsodium
        premake.build(workspace="Yojimbo", targets=["netcode", "reliable", "tlsf", "yojimbo"])

    def package(self):
        copy(self, "LICENCE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        for folder in ("include", "tlsf", "netcode", "reliable", "serialize"):
            # Add a namespace to avoid conflicts with other libraries
            copy(self, "*.h", os.path.join(self.source_folder, folder), os.path.join(self.package_folder, "include", "yojimbo"))
        for lib in ("*.lib", "*.a"):
            copy(self, lib, os.path.join(self.build_folder, "bin"), os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        # Netcode component
        self.cpp_info.components["netcode"].libs = ['netcode']
        self.cpp_info.components["netcode"].requires = ["libsodium::libsodium"]

        # Reliable component
        self.cpp_info.components["reliable"].libs = ['reliable']

        # TLSF component
        self.cpp_info.components["tlsf"].libs = ['tlsf']

        # Yojimbo final compontent
        self.cpp_info.components["yojimbo"].libs = ['yojimbo']
        self.cpp_info.components["yojimbo"].requires = ["netcode", "reliable", "tlsf", "libsodium::libsodium"]
