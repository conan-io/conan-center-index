from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    topics = ("flac", "codec", "audio", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/flac"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", "LPGL-2.1-or-later", "GFDL-1.2")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("ogg/1.3.5")

    def build_requirements(self):
        if Version(self.version) < "1.4.2" and self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("nasm/2.15.05")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()
        if self.settings.arch in ["x86", "x86_64"]:
            envbuild = VirtualBuildEnv(self)
            envbuild.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "src", "share", "getopt", "CMakeLists.txt"),
                        "find_package(Intl)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "COPYING.*", src=self.source_folder,
                                dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        copy(self, "*.h", src=os.path.join(self.source_folder, "include", "share"),
                          dst=os.path.join(self.package_folder, "include", "share"), keep_path=False)
        copy(self, "*.h", src=os.path.join(self.source_folder, "include", "share", "grabbag"),
                          dst=os.path.join(self.package_folder, "include", "share", "grabbag"), keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "flac")

        self.cpp_info.components["libflac"].set_property("cmake_target_name", "FLAC::FLAC")
        self.cpp_info.components["libflac"].set_property("pkg_config_name", "flac")
        self.cpp_info.components["libflac"].libs = ["FLAC"]
        self.cpp_info.components["libflac"].requires = ["ogg::ogg"]

        self.cpp_info.components["libflac++"].set_property("cmake_target_name", "FLAC::FLAC++")
        self.cpp_info.components["libflac++"].set_property("pkg_config_name", "flac++")
        self.cpp_info.components["libflac++"].libs = ["FLAC++"]
        self.cpp_info.components["libflac++"].requires = ["libflac"]
        if not self.options.shared:
            self.cpp_info.components["libflac"].defines = ["FLAC__NO_DLL"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libflac"].system_libs += ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "flac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "flac"
        self.cpp_info.names["cmake_find_package"] = "FLAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FLAC"
        self.cpp_info.components["libflac"].names["cmake_find_package"] = "FLAC"
        self.cpp_info.components["libflac"].names["cmake_find_package_multi"] = "FLAC"
        self.cpp_info.components["libflac++"].names["cmake_find_package"] = "FLAC++"
        self.cpp_info.components["libflac++"].names["cmake_find_package_multi"] = "FLAC++"
