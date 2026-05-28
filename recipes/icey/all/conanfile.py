from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=2.1.0"


class IceyConan(ConanFile):
    name = "icey"
    package_type = "library"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://0state.com/icey/"
    description = "C++20 media stack and libwebrtc alternative for real-time video, signalling, TURN, and media servers"
    topics = ("networking", "webrtc", "ffmpeg", "media", "http", "websocket", "stun", "turn", "c++20")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ffmpeg": [True, False],
        "with_opencv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ffmpeg": False,
        "with_opencv": False,
    }
    implements = ["auto_shared_fpic"]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan handle the C++ standard version, instead of hardcoding it in the CMakeLists.txt
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 20)", "")

    def requirements(self):
        # icy/crypto/cipher.h:20 <openssl/evp.h>
        self.requires("openssl/[>=3.0 <4]", transitive_headers=True)
        # icy/error.h:17 #include "uv.h"
        self.requires("libuv/[>=1.48 <2]", transitive_headers=True)
        # icy/http/parser.h:16 #include <llhttp.h>
        self.requires("llhttp/[>=9.2 <10]", transitive_headers=True)
        # icy/archo/zipfile.h:23 #include <minizip/unzip.h>
        self.requires("minizip/[>=1.3 <2]", transitive_headers=True)
        # icy/json/json.h:19 #include <nlohmann/json.hpp>
        self.requires("nlohmann_json/[~3.11]", transitive_headers=True)
        if self.options.with_ffmpeg:
            # icy/av/ffmpeg.h:24 #include <libavcodec/avcodec.h>
            self.requires("ffmpeg/[>=5.0 <8]", transitive_headers=True)
        if self.options.with_opencv:
            self.requires("opencv/[>=4.5 <5]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_SOLUTION_FOLDERS"] = False
        tc.cache_variables["ENABLE_LOGGING"] = False
        tc.cache_variables["ENABLE_NATIVE_ARCH"] = False
        tc.cache_variables["USE_SYSTEM_DEPS"] = True
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_SAMPLES"] = False
        tc.cache_variables["BUILD_APPLICATIONS"] = False
        tc.cache_variables["BUILD_FUZZERS"] = False
        tc.cache_variables["BUILD_BENCHMARKS"] = False
        tc.cache_variables["BUILD_ALPHA"] = False
        tc.cache_variables["WITH_LIBDATACHANNEL"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["WITH_FFMPEG"] = self.options.with_ffmpeg
        tc.cache_variables["WITH_OPENCV"] = self.options.with_opencv
        tc.generate()

    def validate(self):
        check_min_cppstd(self, 20)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["base"].set_property("cmake_target_name", "icey::base")
        self.cpp_info.components["base"].libs = ["icy_base"]
        self.cpp_info.components["base"].requires = ["libuv::libuv"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["base"].system_libs = ["pthread", "m", "dl", "rt"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["base"].frameworks = ["Foundation", "AVFoundation"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["base"].system_libs = ["ws2_32", "iphlpapi", "psapi", "userenv"]

        self.cpp_info.components["archo"].set_property("cmake_target_name", "icey::archo")
        self.cpp_info.components["archo"].libs = ["icy_archo"]
        self.cpp_info.components["archo"].requires = ["base", "minizip::minizip"]

        self.cpp_info.components["av"].set_property("cmake_target_name", "icey::av")
        self.cpp_info.components["av"].libs = ["icy_av"]
        self.cpp_info.components["av"].requires = ["base"]
        if self.options.with_ffmpeg:
            self.cpp_info.components["av"].requires.append("ffmpeg::ffmpeg")
        if self.options.with_opencv:
            self.cpp_info.components["av"].requires.append("opencv::opencv")

        self.cpp_info.components["crypto"].set_property("cmake_target_name", "icey::crypto")
        self.cpp_info.components["crypto"].libs = ["icy_crypto"]
        self.cpp_info.components["crypto"].requires = ["base", "openssl::openssl"]

        self.cpp_info.components["net"].set_property("cmake_target_name", "icey::net")
        self.cpp_info.components["net"].libs = ["icy_net"]
        self.cpp_info.components["net"].requires = ["base", "crypto", "openssl::openssl"]

        self.cpp_info.components["http"].set_property("cmake_target_name", "icey::http")
        self.cpp_info.components["http"].libs = ["icy_http"]
        self.cpp_info.components["http"].requires = ["base", "net", "crypto", "llhttp::llhttp", "openssl::openssl"]

        self.cpp_info.components["json"].set_property("cmake_target_name", "icey::json")
        self.cpp_info.components["json"].libs = ["icy_json"]
        self.cpp_info.components["json"].requires = ["base", "nlohmann_json::nlohmann_json"]

        self.cpp_info.components["sched"].set_property("cmake_target_name", "icey::sched")
        self.cpp_info.components["sched"].libs = ["icy_sched"]
        self.cpp_info.components["sched"].requires = ["base", "json"]

        self.cpp_info.components["speech"].set_property("cmake_target_name", "icey::speech")
        self.cpp_info.components["speech"].libs = ["icy_speech"]
        self.cpp_info.components["speech"].requires = ["base", "av", "json"]

        self.cpp_info.components["stun"].set_property("cmake_target_name", "icey::stun")
        self.cpp_info.components["stun"].libs = ["icy_stun"]
        self.cpp_info.components["stun"].requires = ["base", "net", "crypto", "openssl::openssl"]

        self.cpp_info.components["symple"].set_property("cmake_target_name", "icey::symple")
        self.cpp_info.components["symple"].libs = ["icy_symple"]
        self.cpp_info.components["symple"].requires = ["base", "crypto", "net", "http", "json", "openssl::openssl"]

        self.cpp_info.components["turn"].set_property("cmake_target_name", "icey::turn")
        self.cpp_info.components["turn"].libs = ["icy_turn"]
        self.cpp_info.components["turn"].requires = ["base", "net", "stun", "crypto"]

        self.cpp_info.components["vision"].set_property("cmake_target_name", "icey::vision")
        self.cpp_info.components["vision"].libs = ["icy_vision"]
        self.cpp_info.components["vision"].requires = ["base", "av", "json"]
