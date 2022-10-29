from conan import ConanFile
from conan.tools.files import get, apply_conandata_patches, rmdir, save, export_conandata_patches
from conans import CMake
import functools
import os
import textwrap

required_conan_version = ">=1.52.0"


class QarchiveConan(ConanFile):
    name = "qarchive"
    license = "BSD-3-Clause"
    homepage = "https://antonyjr.in/QArchive/"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "QArchive is a cross-platform C++ library that modernizes libarchive, "
        "This library helps you to extract and compress archives supported by libarchive"
    )
    topics = ("qt", "compress", "libarchive")

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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libarchive/3.6.1")
        self.requires("qt/5.15.6")

    def build_requirements(self):
        self.build_requires("cmake/3.24.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"QArchive": "QArchive::QArchive"}
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
        self.cpp_info.set_property("cmake_file_name", "QArchive")
        self.cpp_info.set_property("cmake_target_name", "QArchive")
        self.cpp_info.set_property("pkg_config_name", "QArchive")
        self.cpp_info.libs = ["QArchive"]
        self.cpp_info.includedirs = [os.path.join("include", "QArchive")]

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "QArchive"
        self.cpp_info.names["cmake_find_package_multi"] = "QArchive"
        self.cpp_info.names["pkg_config"] = "QArchive"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
