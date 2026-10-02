import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.19.0"


class YojimboConan(ConanFile):
    name = "yojimbo"
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mas-bandwidth/yojimbo"
    topics = ("game", "udp", "protocol", "client-server", "multiplayer-game-server")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # yojimbo bundles a pruned libsodium, but YOJIMBO_SYSTEM_SODIUM=ON links an
        # external one instead so the bundled copy is never compiled. Keeping libsodium
        # unvendored is deliberate: a vendored crypto copy inside this package would not
        # receive libsodium security updates through Conan.
        self.requires("libsodium/1.0.20", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Link the libsodium supplied by Conan rather than yojimbo's bundled subset.
        tc.cache_variables["YOJIMBO_SYSTEM_SODIUM"] = True
        # netcode and reliable have no Conan Center packages, so they are built from
        # yojimbo's own vendored sources. YOJIMBO_SYSTEM_DEPS would look for external
        # ones and fail.
        tc.cache_variables["YOJIMBO_SYSTEM_DEPS"] = False
        tc.cache_variables["YOJIMBO_BUILD_TESTS"] = False
        tc.cache_variables["YOJIMBO_INSTALL"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        # netcode and reliable are separate archives that libyojimbo links against, and
        # upstream's install() rule covers only the yojimbo target, so build them
        # explicitly and copy them in package(). tlsf is NOT built or packaged: since
        # 1.8.0 upstream compiles tlsf.c directly into libyojimbo, and the standalone
        # tlsf target exists only for development builds from the source tree.
        cmake.build(target="netcode")
        cmake.build(target="reliable")
        cmake.build(target="yojimbo")

    def package(self):
        copy(self, "LICENCE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Upstream installs only include/*.h. Consumers of yojimbo's public headers also
        # need the vendored C headers those pull in (netcode.h for netcode_address_t,
        # serialize.h for the serialisation macros), so copy them alongside.
        for folder in ("netcode", "reliable", "serialize"):
            copy(self, "*.h", os.path.join(self.source_folder, folder),
                 os.path.join(self.package_folder, "include"))
        # Copy the three archives by name rather than globbing *.a: upstream also
        # defines a standalone `tlsf` target for source-tree development, and a blanket
        # glob picks up libtlsf.a and ships a stray archive that no component declares.
        for stem in ("netcode", "reliable", "yojimbo"):
            for pattern in (f"lib{stem}.a", f"{stem}.lib"):
                copy(self, pattern, self.build_folder,
                     os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        # netcode component -- the UDP protocol layer; needs libsodium for its AEAD.
        self.cpp_info.components["netcode"].libs = ["netcode"]
        self.cpp_info.components["netcode"].requires = ["libsodium::libsodium"]
        if self.settings.os == "Windows":
            self.cpp_info.components["netcode"].system_libs = ["Ws2_32", "Iphlpapi"]

        # reliable component -- packet acknowledgement.
        self.cpp_info.components["reliable"].libs = ["reliable"]

        # yojimbo itself. No separate tlsf component since 1.8.0: tlsf.c is compiled into
        # libyojimbo, so a consumer linking yojimbo already has it.
        self.cpp_info.components["yojimbo"].libs = ["yojimbo"]
        self.cpp_info.components["yojimbo"].requires = [
            "netcode", "reliable", "libsodium::libsodium",
        ]
        if self.settings.os != "Windows":
            # ceil/floor in the reliable-ordered channel.
            self.cpp_info.components["yojimbo"].system_libs = ["m"]
