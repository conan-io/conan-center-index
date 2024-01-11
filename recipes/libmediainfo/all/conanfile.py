from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "23.11":
            # https://github.com/MediaArea/MediaInfoLib/commit/3bc1fa4c1ea4f15abe053d620b6b585cd8c01998
            return 11
        return None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libzen/0.4.41", transitive_headers=True, transitive_libs=True)
        self.requires("tinyxml2/10.0.0")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.compiler.cppstd and self._min_cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if not self.dependencies["libzen"].options.enable_unicode:
            raise ConanInvalidConfiguration("This package requires libzen with unicode support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self._min_cppstd and not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
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

        replace_in_file(self, os.path.join(self.source_folder, "Project", "CMake", "CMakeLists.txt"),
                        "if(MSVC AND BUILD_SHARED_LIBS)", "if(0)")
        # CMake: remove use of LOCATION property"
        replace_in_file(self, os.path.join(self.source_folder, "Project", "CMake", "CMakeLists.txt"),
                        "set(ZLIB_LIBRARIES", "# set(ZLIB_LIBRARIES")

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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"mediainfo": "MediaInfoLib::MediaInfoLib"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

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

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "MediaInfoLib"
        self.cpp_info.names["cmake_find_package_multi"] = "MediaInfoLib"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
