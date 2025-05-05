from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class SoundTouchConan(ConanFile):
    name = "soundtouch"
    description = "an open-source audio processing library that allows changing the sound tempo, pitch and playback rate parameters independently"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/soundtouch/soundtouch"
    topics = ("audio", "processing", "tempo", "pitch", "playback")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "integer_samples": [True, False],
        "with_openmp": [True, False],
        "with_dll": [True, False],
        "with_util": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "integer_samples": False,
        "with_openmp": False,
        "with_dll": False,
        "with_util": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["INTEGER_SAMPLES"] = self.options.integer_samples
        tc.cache_variables["SOUNDTOUCH_DLL"] = self.options.with_dll
        tc.cache_variables["SOUNDSTRETCH"] = self.options.with_util
        tc.cache_variables["OPENMP"] = self.options.with_openmp
        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        tc.blocks["cmake_flags_init"].template = tc.blocks["cmake_flags_init"].template + """
               string(APPEND CMAKE_CXX_FLAGS_INIT " -fno-finite-math-only")
               string(APPEND CMAKE_C_FLAGS_INIT " -fno-finite-math-only")
           """
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING.TXT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SoundTouch")

        self.cpp_info.components["_soundtouch"].set_property("cmake_target_name", "SoundTouch::SoundTouch")
        self.cpp_info.components["_soundtouch"].set_property("pkg_config_name", "soundtouch")
        self.cpp_info.components["_soundtouch"].libs = ["SoundTouch"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_soundtouch"].system_libs.append("m")
        if not self.options.shared and self.options.with_openmp:
            openmp_flags = []
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            self.cpp_info.components["_soundtouch"].sharedlinkflags = openmp_flags
            self.cpp_info.components["_soundtouch"].exelinkflags = openmp_flags

        if self.options.with_dll:
            self.cpp_info.components["SoundTouchDLL"].set_property("cmake_target_name", "SoundTouch::SoundTouchDLL")
            self.cpp_info.components["SoundTouchDLL"].libs = ["SoundTouchDLL"]
            self.cpp_info.components["SoundTouchDLL"].requires = ["_soundtouch"]

        if self.options.with_util:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SoundTouch"
        self.cpp_info.names["cmake_find_package_multi"] = "SoundTouch"
        self.cpp_info.components["_soundtouch"].names["cmake_find_package"] = "SoundTouch"
        self.cpp_info.components["_soundtouch"].names["cmake_find_package_multi"] = "SoundTouch"
        self.cpp_info.names["pkg_config"] = "SoundTouch"
        if self.options.with_dll:
            self.cpp_info.components["SoundTouchDLL"].names["cmake_find_package"] = "SoundTouchDLL"
            self.cpp_info.components["SoundTouchDLL"].names["cmake_find_package_multi"] = "SoundTouchDLL"

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("mvec")
