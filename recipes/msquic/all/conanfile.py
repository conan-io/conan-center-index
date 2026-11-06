from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime
import os

required_conan_version = ">=2.4.0"


class MsQuicConan(ConanFile):
    name = "msquic"
    package_type = "library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, C implementation of the IETF QUIC protocol"
    homepage = "https://github.com/microsoft/msquic"
    topics = ("quic", "networking", "protocol", "microsoft", "ietf")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]
    languages = "C", "C++"

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["xdp-for-windows"], strip_root=True,
            destination=os.path.join(self.source_folder, "submodules", "xdp-for-windows"))
        # Static builds merge every linked static lib into libmsquic.a and can't handle Conan's generator
        # expressions, so OpenSSL is only linked here for shared builds
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "target_link_libraries(OpenSSLQuic INTERFACE ${OPENSSL_SSL_LIBRARY} ${OPENSSL_CRYPTO_LIBRARY})",
                        "if(BUILD_SHARED_LIBS)\n"
                        "    target_link_libraries(OpenSSLQuic INTERFACE ${OPENSSL_LIBRARIES})\n"
                        "endif()")
        replace_in_file(self, os.path.join(self.source_folder, "src", "inc", "CMakeLists.txt"),
                        "target_compile_options(warnings INTERFACE ${QUIC_WARNING_FLAGS})",
                        "")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os != "Windows":
            # Windows uses Schannel by default
            self.requires("openssl/[>=3.5 <4]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QUIC_BUILD_TOOLS"] = False
        tc.cache_variables["QUIC_BUILD_TEST"] = False
        tc.cache_variables["QUIC_BUILD_PERF"] = False
        tc.cache_variables["QUIC_BUILD_SHARED"] = self.options.shared
        if self.settings.os != "Windows":
            # Upstream defaults to a bundled quictls fork, which rejects external OpenSSL
            tc.cache_variables["QUIC_TLS_LIB"] = "openssl"
            tc.cache_variables["QUIC_USE_EXTERNAL_OPENSSL"] = True
        # Upstream defaults both to ON and then overwrites CMAKE_MSVC_RUNTIME_LIBRARY
        # after project(), which forces /MT even when compiler.runtime is dynamic.
        # PARTIAL implies STATIC, so it must stay off for /MD to take effect.
        tc.cache_variables["QUIC_STATIC_LINK_CRT"] = is_msvc_static_runtime(self)
        tc.cache_variables["QUIC_STATIC_LINK_PARTIAL_CRT"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"),
             excludes="submodules/*")
        if self.settings.os == "Windows":
            copy(self, "LICENSE", src=os.path.join(self.source_folder, "submodules", "xdp-for-windows"),
                 dst=os.path.join(self.package_folder, "licenses", "xdp-for-windows"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # Installed as part of the exported targets of the shared build, not meant to be consumed
        rm(self, "*msquic_platform*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["msquic"]
        if not self.options.shared:
            self.cpp_info.defines = ["QUIC_BUILD_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
            self.cpp_info.defines.append("CX_PLATFORM_LINUX")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]
            self.cpp_info.defines.append("CX_PLATFORM_DARWIN")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "ws2_32", "schannel", "ntdll", "bcrypt", "ncrypt", "crypt32",
                "iphlpapi", "advapi32", "secur32", "wbemuuid", "winmm", "onecore",
            ]
