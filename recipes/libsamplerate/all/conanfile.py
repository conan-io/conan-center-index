from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.3"


class LibsamplerateConan(ConanFile):
    name = "libsamplerate"
    description = (
        "libsamplerate (also known as Secret Rabbit Code) is a library for "
        "performing sample rate conversion of audio data."
    )
    license = "BSD-2-Clause"
    topics = ("libsamplerate", "audio", "resample-audio-files")
    homepage = "https://github.com/libsndfile/libsamplerate"
    url = "https://github.com/conan-io/conan-center-index"

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
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def build_requirements(self):
        if is_apple_os(self) and self.options.shared and Version(self.version) >= "0.2.2":
            # At least CMake 3.17 (see https://github.com/libsndfile/libsamplerate/blob/0.2.2/src/CMakeLists.txt#L110-L119)
            self.tool_requires("cmake/3.24.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBSAMPLERATE_EXAMPLES"] = False
        tc.variables["LIBSAMPLERATE_INSTALL"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_sources(self):
        # Disable upstream logic about msvc runtime policy, called before conan toolchain resolution
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "cmake_policy(SET CMP0091 OLD)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SampleRate")
        self.cpp_info.set_property("cmake_target_name", "SampleRate::samplerate")
        self.cpp_info.set_property("pkg_config_name", "samplerate")
        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["samplerate"].libs = ["samplerate"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["samplerate"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "SampleRate"
        self.cpp_info.names["cmake_find_package_multi"] = "SampleRate"
        self.cpp_info.names["pkg_config"] = "samplerate"
        self.cpp_info.components["samplerate"].names["cmake_find_package"] = "samplerate"
        self.cpp_info.components["samplerate"].names["cmake_find_package_multi"] = "samplerate"
        self.cpp_info.components["samplerate"].set_property("cmake_target_name", "SampleRate::samplerate")
