from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class PhysfsConan(ConanFile):
    name = "physfs"
    description = (
        "PhysicsFS is a library to provide abstract access to various "
        "archives. It is intended for use in video games."
    )
    license = "Zlib"
    topics = ("physfs", "physicsfs", "file", "filesystem", "io")
    homepage = "https://icculus.org/physfs"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zip": [True, False],
        "sevenzip": [True, False],
        "grp": [True, False],
        "wad": [True, False],
        "hog": [True, False],
        "mvl": [True, False],
        "qpak": [True, False],
        "slb": [True, False],
        "iso9660": [True, False],
        "vdf": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zip": True,
        "sevenzip": True,
        "grp": True,
        "wad": True,
        "hog": True,
        "mvl": True,
        "qpak": True,
        "slb": True,
        "iso9660": True,
        "vdf": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PHYSFS_ARCHIVE_ZIP"] = self.options.zip
        self._cmake.definitions["PHYSFS_ARCHIVE_7Z"] = self.options.sevenzip
        self._cmake.definitions["PHYSFS_ARCHIVE_GRP"] = self.options.grp
        self._cmake.definitions["PHYSFS_ARCHIVE_WAD"] = self.options.wad
        self._cmake.definitions["PHYSFS_ARCHIVE_HOG"] = self.options.hog
        self._cmake.definitions["PHYSFS_ARCHIVE_MVL"] = self.options.mvl
        self._cmake.definitions["PHYSFS_ARCHIVE_QPAK"] = self.options.qpak
        self._cmake.definitions["PHYSFS_ARCHIVE_SLB"] = self.options.slb
        self._cmake.definitions["PHYSFS_ARCHIVE_ISO9660"] = self.options.iso9660
        self._cmake.definitions["PHYSFS_ARCHIVE_VDF"] = self.options.vdf
        self._cmake.definitions["PHYSFS_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["PHYSFS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["PHYSFS_BUILD_TEST"] = False
        self._cmake.definitions["PHYSFS_BUILD_DOCS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._physfs_target: "physfs::physfs"}
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

    @property
    def _physfs_target(self):
        return "physfs" if self.options.shared else "physfs-static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PhysFS")
        self.cpp_info.set_property("cmake_target_name", self._physfs_target)
        self.cpp_info.set_property("pkg_config_name", "physfs")
        suffix = "-static" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["physfs{}".format(suffix)]
        if self.options.shared:
            self.cpp_info.defines.append("PHYSFS_SHARED")
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
            elif tools.is_apple_os(self.settings.os):
                self.cpp_info.frameworks.extend(["Foundation", "IOKit"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PhysFS"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PhysFS"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
