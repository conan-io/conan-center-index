from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class FclConan(ConanFile):
    name = "fcl"
    description = "C++11 library for performing three types of proximity " \
                  "queries on a pair of geometric models composed of triangles."
    license = "BSD-3-Clause"
    topics = ("fcl", "geometry", "collision")
    homepage = "https://github.com/flexible-collision-library/fcl"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_octomap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_octomap": True,
    }

    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        self.requires("eigen/3.4.0")
        self.requires("libccd/2.1")
        if self.options.with_octomap:
            self.requires("octomap/1.9.7")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "fcl {} doesn't properly support shared lib on Windows".format(self.version)
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FCL_ENABLE_PROFILING"] = False
        self._cmake.definitions["FCL_TREAT_WARNINGS_AS_ERRORS"] = False
        self._cmake.definitions["FCL_HIDE_ALL_SYMBOLS"] = False
        self._cmake.definitions["FCL_STATIC_LIBRARY"] = not self.options.shared
        self._cmake.definitions["FCL_USE_X64_SSE"] = False # Let consumer decide to add relevant compile options, fcl doesn't have simd intrinsics
        self._cmake.definitions["FCL_USE_HOST_NATIVE_ARCH"] = False
        self._cmake.definitions["FCL_USE_SSE"] = False
        self._cmake.definitions["FCL_COVERALLS"] = False
        self._cmake.definitions["FCL_COVERALLS_UPLOAD"] = False
        self._cmake.definitions["FCL_WITH_OCTOMAP"] = self.options.with_octomap
        if self.options.with_octomap:
            self._cmake.definitions["OCTOMAP_VERSION"] = self.deps_cpp_info["octomap"].version
            octomap_major, octomap_minor, octomap_patch = self.deps_cpp_info["octomap"].version.split(".")
            self._cmake.definitions["OCTOMAP_MAJOR_VERSION"] = octomap_major
            self._cmake.definitions["OCTOMAP_MINOR_VERSION"] = octomap_minor
            self._cmake.definitions["OCTOMAP_PATCH_VERSION"] = octomap_patch
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["FCL_NO_DEFAULT_RPATH"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fcl": "fcl::fcl"}
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
        self.cpp_info.set_property("cmake_file_name", "fcl")
        self.cpp_info.set_property("cmake_target_name", "fcl")
        self.cpp_info.set_property("pkg_config_name", "fcl")
        self.cpp_info.libs = ["fcl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
