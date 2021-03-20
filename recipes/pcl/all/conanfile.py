from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class PclConan(ConanFile):
    name = "pcl"
    description = "Point Cloud Library"
    license = "BSD-3-Clause"
    homepage = "https://pointclouds.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("pointcloud", "computer-vision", "point-cloud")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_png": [True, False],
        "with_qhull": [True, False],
        "with_cuda": [True, False],
        "with_tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_png": True,
        "with_qhull": True,
        "with_cuda": False,
        "with_tools": False,
    }

    exports = ["CMakeLists.txt"]
    generators = ["cmake", "cmake_find_package", "cmake_find_package_multi"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _check_msvc(self):
        if (tools.msvs_toolset(self) == "v140" or
                self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "15"):
            raise ConanInvalidConfiguration("Unsupported Visual Studio Compiler or Toolset")

    def _check_cxx_standard(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def _check_libcxx_compatibility(self):
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            version = tools.Version(self.settings.compiler.version)
            minimum_version = 6
            if version < minimum_version:
                raise ConanInvalidConfiguration("Clang with libc++ is version %s but must be at least version %s" %
                        (version, minimum_version))

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self._check_msvc()
        self._check_cxx_standard()
        self._check_libcxx_compatibility()
        if self.options.with_qhull:
            # TODO: pcl might switch to reentrant qhull in the next release:
            #       don't forget to check https://github.com/PointCloudLibrary/pcl/pull/4540 when you bump pcl version
            self.options["qhull"].reentrant = False

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")
        self.requires("flann/1.9.1")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_qhull:
            self.requires("qhull/8.0.1")

    def validate(self):
        if self.options.with_qhull and self.options["qhull"].reentrant:
            raise ConanInvalidConfiguration("pcl requires non-reentrant qhull, you must set qhull:reentrant=False")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pcl-pcl-{}".format(self.version), self._source_subfolder)

    def _patch_sources(self):
        cmake_lists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Eigen already included by conan_basic_setup(), we don't want that PCL custom FindEigen injects a system installed eigen
        tools.replace_in_file(cmake_lists, "find_package(Eigen 3.1 REQUIRED)", "")
        # Flann already handled in CMake wrapper
        tools.replace_in_file(cmake_lists, "find_package(FLANN 1.7.0 REQUIRED)", "")
        # Qhull already handled in CMake wrapper
        tools.replace_in_file(cmake_lists, "find_package(Qhull)", "")
        # Temporary hack for https://github.com/conan-io/conan/issues/8206
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "pcl_find_boost.cmake"),
                "find_package(Boost 1.55.0 QUIET COMPONENTS serialization mpi)",
                "find_package(Boost 1.55.0 QUIET OPTIONAL_COMPONENTS serialization)"
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake_definitions = {
            "PCL_BUILD_WITH_BOOST_DYNAMIC_LINKING_WIN32": self.options["boost"].shared
        }

        pcl_config = {
            "BUILD_tools": self.options.with_tools,
            "WITH_OPENMP": self.options.with_openmp,
            "WITH_LIBUSB": False,
            "WITH_PNG": self.options.with_png,
            "WITH_QHULL": self.options.with_qhull,
            "WITH_CUDA": self.options.with_cuda,
            "WITH_VTK": False,
            "WITH_PCAP": False,
            "WITH_OPENGL": False,
            "WITH_OPENNI": False,
            "WITH_OPENNI2": False,
            "WITH_ENSENSO": False,
            "WITH_DAVIDSDK": False,
            "WITH_DSSDK": False,
            "WITH_RSSDK": False,
            "PCL_SHARED_LIBS": self.options.shared,
        }
        pcl_features = {
            "BUILD_kdtree": True,
            "BUILD_octree": True,
            "BUILD_search": True,
            "BUILD_sample_consensus": True,
            "BUILD_filters": True,
            "BUILD_2d": True,
            "BUILD_geometry": True,
            "BUILD_io": True,
            "BUILD_features": True,
            "BUILD_ml": True,
            "BUILD_segmentation": True,
            "BUILD_surface": True,
            "BUILD_module_registration": True,
            "BUILD_module_keypoints": True,
            "BUILD_module_tracking": True,
            "BUILD_recognition": True,
            "BUILD_stereo": True,
        }

        self._cmake = CMake(self)
        self._cmake.definitions.update(cmake_definitions)
        self._cmake.definitions.update(pcl_config)
        self._cmake.definitions.update(pcl_features)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for pattern in ["msvcp*.dll", "vcruntime*.dll", "concrt*.dll"]:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), pattern)

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"PCL_{}_LIBRARIES".format(comp.upper()): "PCL::{}".format(comp) for comp in self._pcl_components.keys()}
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
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _pcl_components(self):
        def png():
            return ["libpng::libpng"] if self.options.with_png else []

        def qhull():
            return ["qhull::qhull"] if self.options.with_qhull else []

        return {
            "common": {"requires": ["eigen::eigen", "boost::boost"]},
            "kdtree": {"requires": ["common", "flann::flann"]},
            "octree": {"requires": ["common"]},
            "search": {"requires": ["common", "kdtree", "octree", "flann::flann"]},
            "sample_consensus": {"requires": ["common", "search"]},
            "filters": {"requires": ["common", "sample_consensus", "search", "kdtree", "octree"]},
            "2d": {"requires": ["common", "filters"], "header_only": True},
            "geometry": {"requires": ["common"], "header_only": True},
            "io": {"requires": ["common", "octree"] + png(), "extra_libs": ["io_ply"]},
            "features": {"requires": ["common", "search", "kdtree", "octree", "filters", "2d"]},
            "ml": {"requires": ["common"]},
            "segmentation": {"requires": ["common", "geometry", "search", "sample_consensus", "kdtree", "octree", "features", "filters", "ml"]},
            "surface": {"requires": ["common", "search", "kdtree", "octree"] + qhull()},
            "registration": {"requires": ["common", "octree", "kdtree", "search", "sample_consensus", "features", "filters"]},
            "keypoints": {"requires": ["common", "search", "kdtree", "octree", "features", "filters"]},
            "tracking": {"requires": ["common", "search", "kdtree", "filters", "octree"]},
            "recognition": {"requires": ["common", "io", "search", "kdtree", "octree", "features", "filters", "registration", "sample_consensus", "ml"]},
            "stereo": {"requires": ["common", "io"]}
        }

    @property
    def _version_suffix(self):
        semver = tools.Version(self.version)
        return "{}.{}".format(semver.major, semver.minor)

    def _lib_name(self, lib):
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            return "pcl_{}d".format(lib)
        return "pcl_{}".format(lib)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PCL"
        self.cpp_info.names["cmake_find_package_multi"] = "PCL"

        def _update_components(components):
            for comp, values in components.items():
                self.cpp_info.components[comp].names["cmake_find_package"] = comp
                self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
                self.cpp_info.components[comp].builddirs.append(self._module_subfolder)
                self.cpp_info.components[comp].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[comp].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                self.cpp_info.components[comp].names["pkg_config"] = "pcl_{}-{}".format(comp, self._version_suffix)
                self.cpp_info.components[comp].includedirs = [os.path.join("include", "pcl-{}".format(self._version_suffix))]
                if not values.get("header_only", False):
                    libs = [comp] + values.get("extra_libs", [])
                    self.cpp_info.components[comp].libs = [self._lib_name(lib) for lib in libs]
                self.cpp_info.components[comp].requires = values["requires"]

        _update_components(self._pcl_components)

        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["common"].system_libs.append("pthread")
            if self.options.with_openmp:
                if self.settings.os == "Linux":
                    if self.settings.compiler == "gcc":
                        self.cpp_info.components["common"].sharedlinkflags.append("-fopenmp")
                        self.cpp_info.components["common"].exelinkflags.append("-fopenmp")
                elif self.settings.os == "Windows":
                    if self.settings.compiler == "Visual Studio":
                        self.cpp_info.components["common"].system_libs.append("delayimp")
                    elif self.settings.compiler == "gcc":
                        self.cpp_info.components["common"].system_libs.append("gomp")

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
