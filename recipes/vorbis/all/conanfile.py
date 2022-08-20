from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class VorbisConan(ConanFile):
    name = "vorbis"
    description = "The VORBIS audio codec library"
    topics = ("vorbis", "audio", "codec")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD-3-Clause"

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

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

    def requirements(self):
        self.requires("ogg/1.3.5")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Vorbis")
        # see https://github.com/conan-io/conan-center-index/pull/4173
        self.cpp_info.set_property("pkg_config_name", "vorbis-all-do-not-use")

        # vorbis
        self.cpp_info.components["vorbismain"].set_property("cmake_target_name", "Vorbis::vorbis")
        self.cpp_info.components["vorbismain"].set_property("pkg_config_name", "vorbis")
        self.cpp_info.components["vorbismain"].libs = ["vorbis"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["vorbismain"].system_libs.append("m")
        self.cpp_info.components["vorbismain"].requires = ["ogg::ogg"]

        # TODO: Upstream VorbisConfig.cmake defines components 'Enc' and 'File',
        # which are related to imported targets Vorbis::vorbisenc and Vorbis::vorbisfile
        # Find a way to emulate this in CMakeDeps. See https://github.com/conan-io/conan/issues/10258

        # vorbisenc
        self.cpp_info.components["vorbisenc"].set_property("cmake_target_name", "Vorbis::vorbisenc")
        self.cpp_info.components["vorbisenc"].set_property("pkg_config_name", "vorbisenc")
        self.cpp_info.components["vorbisenc"].libs = ["vorbisenc"]
        self.cpp_info.components["vorbisenc"].requires = ["vorbismain"]

        # vorbisfile
        self.cpp_info.components["vorbisfile"].set_property("cmake_target_name", "Vorbis::vorbisfile")
        self.cpp_info.components["vorbisfile"].set_property("pkg_config_name", "vorbisfile")
        self.cpp_info.components["vorbisfile"].libs = ["vorbisfile"]
        self.cpp_info.components["vorbisfile"].requires = ["vorbismain"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Vorbis"
        self.cpp_info.names["cmake_find_package_multi"] = "Vorbis"
        self.cpp_info.names["pkg_config"] = "vorbis-all-do-not-use"
        self.cpp_info.components["vorbismain"].names["cmake_find_package"] = "vorbis"
        self.cpp_info.components["vorbismain"].names["cmake_find_package_multi"] = "vorbis"
        self.cpp_info.components["vorbisenc"].names["cmake_find_package"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].names["cmake_find_package_multi"] = "vorbisenc"
        self.cpp_info.components["vorbisfile"].names["cmake_find_package"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].names["cmake_find_package_multi"] = "vorbisfile"
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package_multi"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].requires.append("vorbisenc")
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package"] = "File"
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package_multi"] = "File"
        self.cpp_info.components["vorbisfile-alias"].requires.append("vorbisfile")
