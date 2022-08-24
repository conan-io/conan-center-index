from conan.tools.files import rename
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibmediainfoConan(ConanFile):
    name = "libmediainfo"
    license = ("BSD-2-Clause", "Apache-2.0", "GLPL-2.1+", "GPL-2.0-or-later", "MPL-2.0")
    homepage = "https://mediaarea.net/en/MediaInfo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MediaInfo is a convenient unified display of the most relevant technical and tag data for video and audio files"
    topics = ("libmediainfo", "video", "audio", "metadata", "tag")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libcurl/7.82.0")
        self.requires("libzen/0.4.38")
        self.requires("tinyxml2/9.0.0")
        self.requires("zlib/1.2.12")

    def validate(self):
        if not self.options["libzen"].enable_unicode:
            raise ConanInvalidConfiguration("This package requires libzen with unicode support")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_ZENLIB"] = False
        cmake.definitions["BUILD_ZLIB"] = False
        # Generate a relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        rename(self, "Findtinyxml2.cmake", "FindTinyXML.cmake")
        tools.replace_in_file("FindTinyXML.cmake", "tinyxml2_LIBRARIES", "TinyXML_LIBRARIES")

        # TODO: move this to a patch (see how https://github.com/MediaArea/MediaInfoLib/issues/1408 if addressed by upstream)
        postfix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                postfix += "d"
            elif tools.is_apple_os(self.settings.os):
                postfix += "_debug"
        tools.replace_in_file(os.path.join(self._source_subfolder, "Source", "MediaInfoDLL", "MediaInfoDLL.h"),
                              "MediaInfo.dll",
                              "MediaInfo{}.dll".format(postfix))
        tools.replace_in_file(os.path.join(self._source_subfolder, "Source", "MediaInfoDLL", "MediaInfoDLL.h"),
                              "libmediainfo.0.dylib",
                              "libmediainfo{}.0.dylib".format(postfix))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("License.html", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"mediainfo": "MediaInfoLib::MediaInfoLib"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MediaInfoLib")
        self.cpp_info.set_property("cmake_target_name", "mediainfo")
        self.cpp_info.set_property("pkg_config_name", "libmediainfo")
        postfix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                postfix += "d"
            elif tools.is_apple_os(self.settings.os):
                postfix += "_debug"
        self.cpp_info.libs = ["mediainfo" + postfix]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "MediaInfoLib"
        self.cpp_info.names["cmake_find_package_multi"] = "MediaInfoLib"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "libmediainfo"
