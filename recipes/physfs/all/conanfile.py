from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.51.3"


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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PHYSFS_ARCHIVE_ZIP"] = self.options.zip
        tc.variables["PHYSFS_ARCHIVE_7Z"] = self.options.sevenzip
        tc.variables["PHYSFS_ARCHIVE_GRP"] = self.options.grp
        tc.variables["PHYSFS_ARCHIVE_WAD"] = self.options.wad
        tc.variables["PHYSFS_ARCHIVE_HOG"] = self.options.hog
        tc.variables["PHYSFS_ARCHIVE_MVL"] = self.options.mvl
        tc.variables["PHYSFS_ARCHIVE_QPAK"] = self.options.qpak
        tc.variables["PHYSFS_ARCHIVE_SLB"] = self.options.slb
        tc.variables["PHYSFS_ARCHIVE_ISO9660"] = self.options.iso9660
        tc.variables["PHYSFS_ARCHIVE_VDF"] = self.options.vdf
        tc.variables["PHYSFS_BUILD_STATIC"] = not self.options.shared
        tc.variables["PHYSFS_BUILD_SHARED"] = self.options.shared
        tc.variables["PHYSFS_BUILD_TEST"] = False
        tc.variables["PHYSFS_BUILD_DOCS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._physfs_target: "physfs::physfs"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

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
        suffix = "-static" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = ["physfs{}".format(suffix)]
        if self.options.shared:
            self.cpp_info.defines.append("PHYSFS_SHARED")
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
            elif is_apple_os(self):
                self.cpp_info.frameworks.extend(["Foundation", "IOKit"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PhysFS"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PhysFS"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
