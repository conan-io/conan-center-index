import json
import os
import re
from collections import OrderedDict

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, load, replace_in_file, save, rmdir, apply_conandata_patches

required_conan_version = ">=2.0"


class VtkmConan(ConanFile):
    name = "vtk-m"
    description = "VTK-m is a toolkit of scientific visualization algorithms for emerging processor architectures."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://m.vtk.org/"
    topics = ("scientific", "image", "processing", "visualization", "cuda", "hip", "openmp", "tbb")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_logging": [True, False],
        "enable_gpu_mpi": [True, False],
        "use_double_precision": [True, False],
        "no_debug_assert": [True, False],
        "use_vtk_types": [True, False],
        "use_ascent_types": [True, False],
        "use_64bit_ids": [True, False],
        "with_cuda": [True, False],
        "with_hdf5": [True, False],
        "with_kokkos": [True, False],
        "with_mpi": [True, False],
        "with_openmp": [True, False],
        "with_rendering": ["gl", "egl", "osmesa", False],
        "with_tbb": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_logging": True,
        "enable_gpu_mpi": False,
        "use_double_precision": False,
        "no_debug_assert": True,
        "use_vtk_types": True,  # False by default in the project, but required for VTK
        "use_ascent_types": False,
        "use_64bit_ids": True,
        "with_cuda": False,  # TODO: export CMake modules to handle CUDA dependency
        "with_hdf5": True,
        "with_kokkos": False,  # TODO: not on CCI yet. required for HIP support
        "with_mpi": False,  # TODO: enable after #18980
        "with_openmp": False,  # TODO: enable after #22360
        "with_rendering": False,  # FIXME: missing libglvnd binaries
        "with_tbb": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.no_debug_assert

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_mpi:
            self.options.rm_safe("enable_gpu_mpi")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.5")
        if self.options.with_mpi:
            self.requires("openmpi/4.1.6")
        if self.options.with_openmp:
            self.requires("openmp/system")
        if self.options.with_tbb:
            self.requires("onetbb/2021.10.0")
        if self.options.with_rendering:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")
            if self.options.with_rendering == "egl":
                self.requires("egl/system")
            elif self.options.with_rendering == "osmesa":
                self.requires("mesa-glu/9.0.3")

    # Also contains a modified loguru (like VTK) and lodepng, which cannot be unvendored
    # Other vendored deps as of v2.2.0:
    # - diy
    # - ilcl
    # - optionparser

    def validate(self):
        check_min_cppstd(self, 14)

        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CUDA support is not yet implemented")
        if self.options.with_kokkos:
            raise ConanInvalidConfiguration("Kokkos support is not yet implemented")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "vtkm", "thirdparty", "diy", "vtkmdiy", "cmake", "DIYConfigureMPI.cmake"),
                        "${MPI_CXX_LIBRARIES}", "MPI::MPI_CXX")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VTKm_ENABLE_TESTING"] = False
        tc.variables["VTKm_ENABLE_TESTING_LIBRARY"] = False
        tc.variables["VTKm_VERBOSE_MODULES"] = True
        tc.variables["VTKm_USE_DEFAULT_TYPES_FOR_VTK"] = self.options.use_vtk_types
        tc.variables["VTKm_USE_DEFAULT_TYPES_FOR_ASCENT"] = self.options.use_ascent_types
        tc.variables["VTKm_USE_DOUBLE_PRECISION"] = self.options.use_double_precision
        tc.variables["VTKm_NO_ASSERT"] = self.options.get_safe("no_debug_assert", True)
        tc.variables["VTKm_USE_64BIT_IDS"] = self.options.use_64bit_ids
        tc.variables["VTKm_ENABLE_MPI"] = self.options.with_mpi
        tc.variables["VTKm_ENABLE_GPU_MPI"] = self.options.get_safe("enable_gpu_mpi", False)
        tc.variables["VTKm_ENABLE_OPENMP"] = self.options.with_openmp
        tc.variables["VTKm_ENABLE_TBB"] = self.options.with_tbb
        tc.variables["VTKm_ENABLE_CUDA"] = self.options.with_cuda
        tc.variables["VTKm_ENABLE_KOKKOS"] = self.options.with_kokkos
        tc.variables["VTKm_ENABLE_ANARI"] = False  # not really supported anyway as of v2.2.0
        tc.variables["VTKm_ENABLE_HDF5_IO"] = self.options.with_hdf5
        tc.variables["VTKm_HDF5_IS_PARALLEL"] = self.options.with_hdf5 and self.dependencies["hdf5"].options.parallel
        tc.variables["VTKm_ENABLE_LOGGING"] = self.options.enable_logging
        tc.variables["VTKm_ENABLE_RENDERING"] = bool(self.options.with_rendering)
        tc.variables["VTKm_ENABLE_GL_CONTEXT"] = self.options.with_rendering == "gl"
        tc.variables["VTKm_ENABLE_EGL_CONTEXT"] = self.options.with_rendering == "egl"
        tc.variables["VTKm_ENABLE_OSMESA_CONTEXT"] = self.options.with_rendering == "osmesa"

        # Required for check_type_size() using try_compile() using Conan CMake targets to work
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = self.settings.build_type

        # Drop unnecessary version suffixes from file and directory names
        tc.variables["VTKm_INSTALL_INCLUDE_DIR"] = "include"
        tc.variables["VTKm_INSTALL_CONFIG_DIR"] = "lib/cmake/vtkm"
        tc.variables["VTKm_CUSTOM_LIBRARY_SUFFIX"] = ""
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @staticmethod
    def _remove_duplicates(values):
        return list(OrderedDict.fromkeys(values))

    def _parse_cmake_targets(self, targets_file):
        txt = load(self, targets_file)
        raw_targets = re.findall(r"add_library\((\S+) (\S+) IMPORTED\)", txt)
        targets = {name: {"is_interface": kind == "INTERFACE"} for name, kind in raw_targets}
        props_raw = re.findall(r"set_target_properties\((\S+) PROPERTIES\n((?: *.+\n)+)\)", txt)
        for name, body in props_raw:
            for prop, value in re.findall(r"^ *INTERFACE_(\w+)\b \"(.+)\"$", body, re.M):
                value = value.split(";")
                targets[name][prop.lower()] = value
        return targets

    @property
    def _known_system_libs(self):
        return ["m", "dl", "pthread", "rt", "socket", "nsl", "wsock32", "ws2_32"]

    def _transform_link_libraries(self, values):
        # Converts a list of LINK_LIBRARIES values into a list of component requirements and system_libs.
        requires = []
        system_libs = []
        for v in values:
            # strip "\$<LINK_ONLY:FontConfig::FontConfig>" etc.
            v = re.sub(r"^\\\$<LINK_ONLY:(.*)>$", r"\1", v)
            if not v:
                continue
            if v in self._known_system_libs:
                system_libs.append(v)
            elif v == "Threads::Threads":
                if self.settings.os in ["Linux", "FreeBSD"]:
                    system_libs.append("pthread")
            else:
                requires.append(self._cmake_target_to_conan_requirement(v))
        return requires, system_libs

    def _cmake_target_to_conan_requirement(self, target):
        if target.startswith("vtkm::"):
            return target[6:]
        target_map = {
            "GLEW::GLEW": "glew::glew",
            "HDF5::HDF5": "hdf5::hdf5",
            "MPI::MPI_CXX": "openmpi::ompi-cxx",
            "OpenGL::EGL": "egl::egl",
            "OpenGL::GL": "opengl::opengl",
            "OpenGL::GLU": "mesa-glu::mesa-glu",
            "OpenGL::GLX": "opengl::opengl",
            "OpenGL::OpenGL": "opengl::opengl",
            "OpenMP::OpenMP_CXX": "openmp::openmp",
            "TBB::tbb": "onetbb::libtbb",
        }
        return target_map[target]

    def _cmake_targets_to_conan_components(self, targets_info):
        components = {}
        for target_name, target_info in targets_info.items():
            name = target_name.replace("vtkm::", "")
            component = {}
            if not target_info["is_interface"]:
                component["libs"] = [name if name.startswith("vtkm") else f"vtkm_{name}"]
            for definition in target_info.get("compile_definitions", []):
                if definition.startswith("-D"):
                    definition = definition[2:]
                if "defines" not in component:
                    component["defines"] = []
                component["defines"].append(definition)
            requires, system_libs = self._transform_link_libraries(target_info.get("link_libraries", []))
            requires = self._remove_duplicates(requires)
            if "vtkbuild" in requires:
                requires.remove("vtkbuild")
            if requires:
                component["requires"] = requires
            if system_libs:
                component["system_libs"] = self._remove_duplicates(system_libs)
            if "include_directories" in target_info:
                component["include_dirs"] = [d.replace("${_IMPORT_PREFIX}/", "") for d in target_info["include_directories"]]
            component["target_name"] = target_name
            components[name] = component
        return components

    @property
    def _components_json(self):
        return os.path.join(self.package_folder, "res", "conan_components.json")

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # Generate Conan targets dynamically from VTKmTargets.cmake
        targets = self._parse_cmake_targets(os.path.join(self.package_folder, "lib", "cmake", "vtkm", "VTKmTargets.cmake"))
        components = self._cmake_targets_to_conan_components(targets)

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        save(self, self._components_json, json.dumps(components, indent=2))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VTKm")
        self.cpp_info.set_property("pkg_config_name", "vtkm")

        components = json.loads(load(self, self._components_json))
        for name, info in components.items():
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", info["target_name"])
            component.includedirs = info.get("include_dirs", [])
            component.libs = info.get("libs", [])
            component.defines = info.get("defines", [])
            component.requires = info.get("requires", [])
            component.system_libs = info.get("system_libs", [])

        if "io" in components and self.options.with_hdf5:
            self.cpp_info.components["io"].requires.append("hdf5::hdf5_hl")

        for component_name, component in self.cpp_info.components.items():
            self.output.info(f"COMPONENT: {component_name}")
            if component.libs:
                self.output.info(f" - libs: {component.libs}")
            if component.defines:
                self.output.info(f" - defines: {component.defines}")
            if component.requires:
                self.output.info(f" - requires: {component.requires}")
            if component.system_libs:
                self.output.info(f" - system_libs: {component.system_libs}")
            if component.frameworks:
                self.output.info(f" - frameworks: {component.frameworks}")
