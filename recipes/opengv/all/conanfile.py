from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"

class opengvConan(ConanFile):
    name = "opengv"
    description = "A collection of computer vision methods for solving geometric vision problems"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/laurentkneip/opengv"
    license = "BSD-3-Clause"
    topics = ("computer", "vision", "geometric", "pose", "triangulation", "point-cloud")
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_python_bindings": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "with_python_bindings": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

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

    def validate(self):
        # Disable windows builds since they error out.
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds are not supported by this recipe.")
        #FIXME disable this one CCI has more RAM available
        if (self.settings.compiler == "gcc" and self.options.shared):
                raise ConanInvalidConfiguration("Shared builds not supported with gcc since CCI errors out due to excessive memory usage.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("eigen/3.4.0")
        if self.options.with_python_bindings:
            self.requires("pybind11/2.7.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_PYTHON"] = self.options.with_python_bindings
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        # Use conan's Eigen
        old = """\
            find_package(Eigen REQUIRED)
            set(ADDITIONAL_INCLUDE_DIRS ${EIGEN_INCLUDE_DIRS} ${EIGEN_INCLUDE_DIR}/unsupported)"""

        new = """\
            find_package(Eigen3 REQUIRED)
            set(ADDITIONAL_INCLUDE_DIRS ${Eigen3_INCLUDE_DIRS} ${Eigen3_INCLUDE_DIR}/unsupported)"""

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                            textwrap.dedent(old),
                            textwrap.dedent(new)
        )

        # Use conan's pybind11
        tools.replace_in_file(os.path.join(self._source_subfolder, "python", "CMakeLists.txt"),
                            "add_subdirectory(pybind11)",
                            "find_package(pybind11 REQUIRED)"
        )

        # Let conan handle fPIC / shared
        old = """\
            IF(MSVC)
              set(BUILD_SHARED_LIBS OFF)"""

        new = """\
            IF(1)
              #set(BUILD_SHARED_LIBS OFF)"""

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                            textwrap.dedent(old),
                            textwrap.dedent(new)
        )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"opengv": "opengv::opengv"}
        )

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.with_python_bindings:
            self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3", "dist-packages")
