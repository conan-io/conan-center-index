import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class LibmediainfoConan(ConanFile):
    name = "libmediainfo"
    license = ("BSD-2-Clause", "Apache-2.0", "GLPL-2.1+", "GPL-2.0-or-later", "MPL-2.0")
    homepage = "https://mediaarea.net/en/MediaInfo"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "MediaInfo is a convenient unified display of the most relevant "
        "technical and tag data for video and audio files"
    )
    topics = ("video", "audio", "metadata", "tag")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzen/0.4.41", transitive_headers=True, transitive_libs=True)
        self.requires("tinyxml2/10.0.0")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if Version(self.version) >= "23.11":
            # https://github.com/MediaArea/MediaInfoLib/commit/3bc1fa4c1ea4f15abe053d620b6b585cd8c01998
            check_min_cppstd(self, 11)
        if not self.dependencies["libzen"].options.enable_unicode:
            raise ConanInvalidConfiguration("This package requires libzen with unicode support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_ZENLIB"] = False
        tc.variables["BUILD_ZLIB"] = False
        tc.variables["ZenLib_LIBRARY"] = "zen::zen"
        if Version(self.version) < "22.03":
            # Generate a relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Allow non-cache_variables
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("tinyxml2", "cmake_file_name", "TinyXML")
        deps.set_property("libzen", "cmake_target_name", "zen::zen")
        deps.generate()

    def _patch_sources(self):
        # TODO: move this to a patch (see how https://github.com/MediaArea/MediaInfoLib/issues/1408 is addressed by upstream)
        postfix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                postfix += "d"
            elif is_apple_os(self):
                postfix += "_debug"
        mediainfodll_h = os.path.join(self.source_folder, "Source", "MediaInfoDLL", "MediaInfoDLL.h")
        replace_in_file(self, mediainfodll_h, "MediaInfo.dll", f"MediaInfo{postfix}.dll")
        replace_in_file(self, mediainfodll_h, "libmediainfo.0.dylib", f"libmediainfo{postfix}.0.dylib")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Project", "CMake"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "License.html", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MediaInfoLib")
        self.cpp_info.set_property("cmake_target_name", "mediainfo")
        self.cpp_info.set_property("pkg_config_name", "libmediainfo")

        postfix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                postfix += "d"
            elif is_apple_os(self):
                postfix += "_debug"
        self.cpp_info.libs = [f"mediainfo{postfix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        if self.options.shared:
            self.cpp_info.defines.append("LIBMEDIAINFO_SHARED")
