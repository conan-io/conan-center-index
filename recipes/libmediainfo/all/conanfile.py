from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class LibmediainfoConan(ConanFile):
    name = "libmediainfo"
    license = ("BSD-2-Clause", "Apache-2.0", "GLPL-2.1+", "GPL-2.0-or-later", "MPL-2.0")
    homepage = "https://mediaarea.net/en/MediaInfo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MediaInfo is a convenient unified display of the most relevant technical and tag data for video and audio files"
    topics = ("conan", "libmediainfo", "video", "audio", "metadata", "tag")
    settings = "os",  "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def requirements(self):
        self.requires("libcurl/7.77.0")
        self.requires("libzen/0.4.38")
        self.requires("tinyxml2/8.0.0")
        self.requires("zlib/1.2.11")

    def validate(self):
        if not self.options["libzen"].enable_unicode:
            raise ConanInvalidConfiguration("This package requires libzen with unicode support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_ZENLIB"] = False
        self._cmake.definitions["BUILD_ZLIB"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.rename("Findtinyxml2.cmake", "FindTinyXML.cmake")
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
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        postfix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                postfix += "d"
            elif tools.is_apple_os(self.settings.os):
                postfix += "_debug"
        self.cpp_info.libs = ["mediainfo" + postfix]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "MediaInfoLib"
        self.cpp_info.names["cmake_find_package_multi"] = "MediaInfoLib"
        self.cpp_info.names["pkg_config"] = "libmediainfo"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
