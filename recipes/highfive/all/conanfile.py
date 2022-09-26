from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, save
import os
import textwrap

required_conan_version = ">=1.50.0"


class HighFiveConan(ConanFile):
    name = "highfive"
    description = "HighFive is a modern header-only C++11 friendly interface for libhdf5."
    license = "Boost Software License 1.0"
    topics = ("hdf5", "hdf", "data")
    homepage = "https://github.com/BlueBrain/HighFive"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost": [True, False],
        "with_eigen": [True, False],
        "with_xtensor": [True, False],
        "with_opencv": [True, False],
    }
    default_options = {
        "with_boost": True,
        "with_eigen": True,
        "with_xtensor": True,
        "with_opencv": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hdf5/1.13.1")
        if self.options.with_boost:
            self.requires("boost/1.80.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_xtensor:
            self.requires("xtensor/0.24.2")
        if self.options.with_opencv:
            self.requires("opencv/4.5.5")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_BOOST"] = self.options.with_boost
        tc.variables["USE_EIGEN"] = self.options.with_eigen
        tc.variables["USE_XTENSOR"] = self.options.with_xtensor
        tc.variables["USE_OPENCV"] = self.options.with_opencv
        tc.variables["HIGHFIVE_UNIT_TESTS"] = False
        tc.variables["HIGHFIVE_EXAMPLES"] = False
        tc.variables["HIGHFIVE_BUILD_DOCS"] = False
        tc.variables["HIGHFIVE_USE_INSTALL_DEPS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMake", "HighFiveTargetDeps.cmake"),
            "find_package(Eigen3 NO_MODULE)",
            "find_package(Eigen3 REQUIRED)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMake", "HighFiveTargetDeps.cmake"),
            "EIGEN3_INCLUDE_DIRS",
            "Eigen3_INCLUDE_DIRS",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"HighFive": "HighFive::HighFive"},
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
        self.cpp_info.set_property("cmake_file_name", "HighFive")
        self.cpp_info.set_property("cmake_target_name", "HighFive")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.requires = ["hdf5::hdf5"]
        if self.options.with_boost:
            self.cpp_info.requires.append("boost::headers")
        if self.options.with_eigen:
            self.cpp_info.requires.append("eigen::eigen")
        if self.options.with_xtensor:
            self.cpp_info.requires.append("xtensor::xtensor")
        if self.options.with_opencv:
            self.cpp_info.requires.append("opencv::opencv")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "HighFive"
        self.cpp_info.names["cmake_find_package_multi"] = "HighFive"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
