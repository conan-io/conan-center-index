from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


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

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBSAMPLERATE_EXAMPLES"] = False
        self._cmake.definitions["LIBSAMPLERATE_INSTALL"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build_requirements(self):
        if tools.is_apple_os(self.settings.os) and self.options.shared and tools.Version(self.version) >= "0.2.2":
            self.build_requires("cmake/3.21.3")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

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
