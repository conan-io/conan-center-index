import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name

required_conan_version = ">=2.1"

class libdatachannelConan(ConanFile):
    name = "libdatachannel"
    description = "C/C++ WebRTC network library featuring Data Channels, Media Transport, and WebSockets."
    license = "MPL-2.0"
    topics = ("webrtc", "rtc", "datachannel", "websocket")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paullouisageneau/libdatachannel"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_websocket": [True, False],
        "with_nice": [True, False],
        "with_ssl": ["openssl", "mbedtls", "gnutls"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_websocket": True,
        "with_nice": False,
        "with_ssl": "openssl"
    }

    implements = ["auto_shared_fpic"]

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.with_ssl == "mbedtls":
            self.requires("mbedtls/3.6.2")
        elif self.options.with_ssl == "gnutls":
            self.requires("gnutls/3.8.7")
            if self.options.with_websocket:
                self.requires("nettle/3.9.1")
        self.requires("plog/1.1.10")
        self.requires("usrsctp/0.9.5.0")
        self.requires("libsrtp/2.6.0")
        if self.options.with_nice:
            self.requires("libnice/0.1.21")
        else:
            self.requires("libjuice/1.5.7", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.with_ssl == "mbedtls":
            # dtlstransport.cpp:414:3: error: use of undeclared identifier 'mbedtls_ssl_conf_dtls_srtp_protection_profiles'
            raise ConanInvalidConfiguration("Compilation error with mbedtls. Contributions are welcome.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Let Conan handle fpic
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PREFER_SYSTEM_LIB"] = True
        tc.cache_variables["USE_SYSTEM_SRTP"] = True
        tc.cache_variables["USE_SYSTEM_USRSCTP"] = True
        tc.cache_variables["USE_SYSTEM_PLOG"] = True
        tc.cache_variables["USE_SYSTEM_JSON"] = True
        tc.cache_variables["NO_EXAMPLES"] = True
        tc.cache_variables["NO_TESTS"] = True
        tc.cache_variables["NO_WEBSOCKET"] = not self.options.with_websocket
        tc.cache_variables["USE_NICE"] = self.options.with_nice
        tc.cache_variables["USE_SYSTEM_JUICE"] = not self.options.with_nice
        if self.options.with_ssl == "gnutls":
            tc.cache_variables["USE_GNUTLS"] = True
        elif self.options.with_ssl == "mbedtls":
            tc.cache_variables["USE_MBEDTLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("usrsctp", "cmake_target_name", "Usrsctp::Usrsctp")
        deps.set_property("libsrtp", "cmake_file_name", "libSRTP")
        deps.set_property("libsrtp", "cmake_target_name", "libSRTP::srtp2")
        if self.options.with_ssl == "mbedtls":
            deps.set_property("mbedtls", "cmake_target_name", "MbedTLS::MbedTLS")
        elif self.options.with_ssl == "gnutls" and self.options.with_websocket:
            deps.set_property("nettle", "cmake_file_name", "Nettle")
            deps.set_property("nettle", "cmake_target_name", "Nettle::Nettle")
        if self.options.with_nice:
            deps.set_property("libnice", "cmake_file_name", "LibNice")
            deps.set_property("libnice", "cmake_target_name", "LibNice::LibNice")
        elif not self.options.shared:
            # Targetname is LibJuice::LibJuiceStatic for static, but upstream makes no distinction
            deps.set_property("libjuice", "cmake_target_name", "LibJuice::LibJuice")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        suffix = ""
        if is_msvc(self) and self.settings.build_type == "Debug":
            suffix = "d"
        self.cpp_info.libs = ["datachannel" + suffix]
        self.cpp_info.set_property("cmake_file_name", "LibDataChannel")
        self.cpp_info.set_property("cmake_target_name", "LibDataChannel::LibDataChannel")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

        if not self.options.shared:
            self.cpp_info.defines.append("RTC_STATIC")

        self.cpp_info.defines.append("RTC_ENABLE_WEBSOCKET=" + ("1" if self.options.with_websocket else "0"))
        # This is True by default, and the recipe currently does not model it
        self.cpp_info.defines.append("RTC_ENABLE_MEDIA=1")

