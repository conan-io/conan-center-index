import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, replace_in_file, load, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ColmapConan(ConanFile):
    name = "colmap"
    description = ("COLMAP is a general-purpose Structure-from-Motion (SfM) and "
                   "Multi-View Stereo (MVS) pipeline with a graphical and command-line interface.")
    license = "BSD-3-Clause"
    homepage = "https://colmap.github.io/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "structure-from-motion", "multi-view-stereo", "3d-reconstruction", "photogrammetry")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "cgal": [True, False],
        "cuda": [True, False],
        "gui": [True, False],
        "ipo": [True, False],
        "openmp": [True, False],
        "tools": [True, False],
        "cuda_architectures": ["native", "all-major", "all", "ANY"],
    }
    default_options = {
        "fPIC": True,
        "cgal": True,
        "cuda": False,
        "gui": False,
        "ipo": True,
        "openmp": True,
        "tools": True,
        "cuda_architectures": "all-major",
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        copy(self, "colmap-conan-vars.cmake.in", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.cuda:
            del self.options.cuda_architectures

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.84.0", transitive_headers=True, transitive_libs=True)
        # Ceres 2.2.0 is not compatible as of v3.10
        self.requires("ceres-solver/2.1.0", transitive_headers=True, transitive_libs=True)
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("flann/1.9.2", transitive_headers=True, transitive_libs=True)
        self.requires("freeimage/3.18.0")
        self.requires("glog/0.6.0", transitive_headers=True, transitive_libs=True)
        self.requires("metis/5.2.1")
        self.requires("sqlite3/3.45.3", transitive_headers=True, transitive_libs=True)
        self.requires("lz4/1.9.4")
        if self.options.openmp:
            self.requires("openmp/system", transitive_headers=True, transitive_libs=True)
        if self.options.cgal:
            self.requires("cgal/5.6.1")
        if self.options.gui:
            self.requires("qt/5.15.13", transitive_headers=True, transitive_libs=True)
        if self.options.gui or self.options.cuda:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")
        # TODO: unvendor VLFeat, PoissonRecon, LSD, SiftGPU
        # self.requires("vlfeat/0.9.21", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if self.options.cuda:
            self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CCACHE_ENABLED"] = False
        tc.cache_variables["CGAL_ENABLED"] = self.options.cgal
        tc.cache_variables["CUDA_ENABLED"] = self.options.cuda
        tc.cache_variables["GUI_ENABLED"] = self.options.gui
        tc.cache_variables["IPO_ENABLED"] = self.options.ipo
        tc.cache_variables["OPENGL_ENABLED"] = self.options.gui
        tc.cache_variables["OPENMP_ENABLED"] = self.options.openmp
        tc.cache_variables["SIMD_ENABLED"] = True  # only applied to VLFeat and when on x86
        tc.cache_variables["TESTS_ENABLED"] = False
        tc.cache_variables["CMAKE_CUDA_ARCHITECTURES"] = self.options.get_safe("cuda_architectures", "")
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("cgal", "cmake_file_name", "CGAL")
        deps.set_property("cgal", "cmake_target_aliases", ["CGAL"])
        deps.set_property("flann", "cmake_file_name", "FLANN")
        deps.set_property("flann", "cmake_target_name", "flann")
        deps.set_property("freeimage", "cmake_file_name", "FreeImage")
        deps.set_property("freeimage::FreeImage", "cmake_target_name", "freeimage::FreeImage")
        deps.set_property("glew", "cmake_file_name", "Glew")
        deps.set_property("glew", "cmake_target_name", "GLEW::GLEW")
        deps.set_property("glog", "cmake_file_name", "Glog")
        deps.set_property("glog", "cmake_target_name", "glog::glog")
        deps.set_property("lz4", "cmake_file_name", "LZ4")
        deps.set_property("lz4", "cmake_target_name", "lz4")
        deps.set_property("metis", "cmake_file_name", "Metis")
        deps.set_property("metis", "cmake_target_name", "metis")
        deps.generate()

        VirtualBuildEnv(self).generate()

        # FIXME: this is a hack for Freeimage and Metis transitive dep shared libs not being found for some reason
        VirtualRunEnv(self).generate(scope="build")

    def _patch_sources(self):
        for module in self.source_path.joinpath("cmake").glob("Find*.cmake"):
            if module.name != "FindDependencies.cmake":
                module.unlink()
        find_dependencies = self.source_path.joinpath("cmake", "FindDependencies.cmake")
        replace_in_file(self, find_dependencies, " QUIET", " REQUIRED")

        if not self.options.gui and not self.options.cuda:
            # OpenGL and GLEW are not actually being used in this case
            replace_in_file(self, find_dependencies, "find_package(Glew", "# find_package(Glew")
            replace_in_file(self, find_dependencies, "find_package(OpenGL", "# find_package(OpenGL")

        if not self.options.tools:
            replace_in_file(self, os.path.join(self.source_folder, "src", "colmap", "exe", "CMakeLists.txt"),
                            "COLMAP_ADD_EXECUTABLE(", "message(TRACE ")
            replace_in_file(self, os.path.join(self.source_folder, "src", "colmap", "exe", "CMakeLists.txt"),
                            "set_target_properties(colmap_main ", "# set_target_properties(colmap_main ")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _write_cmake_module(self):
        content = load(self, os.path.join(self.export_sources_folder, "colmap-conan-vars.cmake.in"))
        content = content.replace("@COLMAP_VERSION@", self.version)
        content = content.replace("@CUDA_ENABLED@", "TRUE" if self.options.cuda else "FALSE")
        save(self, os.path.join(self.package_folder, "lib", "cmake", "colmap-conan-vars.cmake"), content)

    def package(self):
        copy(self, "COPYING.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        self._write_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "colmap")
        self.cpp_info.set_property("cmake_target_name", "colmap::colmap")

        module_rel_path = os.path.join("lib", "cmake", "colmap-conan-vars.cmake")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.set_property("cmake_build_modules", [module_rel_path])
        self.cpp_info.build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [module_rel_path]

        def _add_component(name, requires):
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", f"colmap::colmap_{name}")
            component.libs = [f"colmap_{name}"]
            component.requires = requires
            return component

        util = _add_component("util", requires=["boost::headers", "boost::filesystem", "eigen::eigen", "glog::glog", "sqlite3::sqlite3"])
        _add_component("controllers", requires=["util", "estimators", "feature", "image", "math", "mvs", "retrieval", "sfm", "scene",
                                                "ceres-solver::ceres", "boost::program_options"])
        _add_component("estimators", requires=["util", "math", "feature_types", "geometry", "sensor", "image", "scene", "optim", "ceres-solver::ceres"])
        exe = _add_component("exe", requires=["util", "controllers", "estimators", "geometry", "optim", "scene"])
        _add_component("feature_types", requires=["util"])
        feature = _add_component("feature", requires=["util", "feature_types", "geometry", "retrieval", "scene", "math", "sensor", "vlfeat", "flann::flann", "lz4::lz4"])
        _add_component("geometry", requires=["util", "math"])
        _add_component("image", requires=["util", "sensor", "scene", "lsd"])
        _add_component("math", requires=["util", "metis::metis", "boost::graph"])
        mvs = _add_component("mvs", requires=["util", "scene", "sensor", "image", "poisson_recon"])
        _add_component("optim", requires=["math"])
        _add_component("retrieval", requires=["math", "estimators", "optim", "flann::flann", "lz4::lz4"])
        _add_component("scene", requires=["util", "sensor", "feature_types", "geometry"])
        _add_component("sensor", requires=["util", "vlfeat", "freeimage::FreeImage", "ceres-solver::ceres"])
        _add_component("sfm", requires=["util", "geometry", "image", "scene", "estimators"])
        _add_component("lsd", requires=[])
        poisson_recon = _add_component("poisson_recon", requires=[])
        vlfeat = _add_component("vlfeat", requires=[])

        if self.options.cgal:
            mvs.requires.append("cgal::cgal")

        if self.options.gui:
            _add_component("ui", requires=["util", "image", "scene", "controllers", "qt::qtCore", "qt::qtOpenGL", "qt::qtWidgets"])
            util.requires.extend(["qt::Core", "qt::OpenGL", "opengl::opengl"])
            feature.requires.extend(["qt::qtWidgets"])
            exe.requires.extend(["ui"])

        if self.options.openmp:
            poisson_recon.requires.append("openmp::openmp")
            vlfeat.requires.append("openmp::openmp")

        if self.options.cuda:
            # CUDA dependencies are exported in the CMake module
            _add_component("util_cuda", requires=["util"])
            _add_component("mvs_cuda", requires=["mvs", "util_cuda"])
            exe.requires.extend(["util_cuda", "mvs_cuda"])

        if self.options.gui or self.options.cuda:
            _add_component("sift_gpu", requires=["opengl::opengl", "glew::glew"])
            feature.requires.extend(["sift_gpu"])
