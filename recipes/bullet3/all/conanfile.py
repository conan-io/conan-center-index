from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import glob
import os
import textwrap

required_conan_version = ">=1.50.0"


class Bullet3Conan(ConanFile):
    name = "bullet3"
    description = (
        "Bullet Physics SDK: real-time collision detection and multi-physics "
        "simulation for VR, games, visual effects, robotics, machine learning etc."
    )
    homepage = "https://github.com/bulletphysics/bullet3"
    topics = ("bullet", "physics", "simulation", "robotics", "kinematics", "engine")
    license = "ZLIB"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bullet3": [True, False],
        "graphical_benchmark": [True, False],
        "double_precision": [True, False],
        "bt2_thread_locks": [True, False],
        "soft_body_multi_body_dynamics_world": [True, False],
        "network_support": [True, False],
        "extras": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bullet3": True,
        "graphical_benchmark": False,
        "double_precision": False,
        "bt2_thread_locks": False,
        "soft_body_multi_body_dynamics_world": False,
        "network_support": False,
        "extras": False,
    }

    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration("Shared libraries on Visual Studio not supported")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BULLET3"] = self.options.bullet3
        tc.variables["INSTALL_LIBS"] = True
        tc.variables["USE_GRAPHICAL_BENCHMARK"] = self.options.graphical_benchmark
        tc.variables["USE_DOUBLE_PRECISION"] = self.options.double_precision
        tc.variables["BULLET2_MULTITHREADING"] = self.options.bt2_thread_locks
        tc.variables["USE_SOFT_BODY_MULTI_BODY_DYNAMICS_WORLD"] = self.options.soft_body_multi_body_dynamics_world
        tc.variables["BUILD_ENET"] = self.options.network_support
        tc.variables["BUILD_CLSOCKET"] = self.options.network_support
        tc.variables["BUILD_CPU_DEMOS"] = False
        tc.variables["BUILD_OPENGL3_DEMOS"] = False
        tc.variables["BUILD_BULLET2_DEMOS"] = False
        tc.variables["BUILD_EXTRAS"] = self.options.extras
        tc.variables["BUILD_UNIT_TESTS"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if Version(self.version) < "3.21":
            # silence warning
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0115"] = "OLD"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for cmake_file in glob.glob(os.path.join(self.package_folder, self._module_subfolder, "*.cmake")):
            if os.path.basename(cmake_file) != "UseBullet.cmake":
                os.remove(cmake_file)
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(BULLET_FOUND 1)
            set(BULLET_USE_FILE "lib/cmake/bullet/UseBullet.cmake")
            set(BULLET_DEFINITIONS {" ".join(self._bullet_definitions)})
            set(BULLET_INCLUDE_DIR ${{Bullet_INCLUDE_DIR}}
                                   ${{Bullet_INCLUDE_DIR_RELEASE}}
                                   ${{Bullet_INCLUDE_DIR_RELWITHDEBINFO}}
                                   ${{Bullet_INCLUDE_DIR_MINSIZEREL}}
                                   ${{Bullet_INCLUDE_DIR_DEBUG}})
            set(BULLET_INCLUDE_DIRS ${{BULLET_INCLUDE_DIR}})
            set(BULLET_LIBRARIES Bullet::Bullet)
            set(BULLET_LIBRARY_DIRS ${{Bullet_LIB_DIRS}}
                                    ${{Bullet_LIB_DIRS_RELEASE}}
                                    ${{Bullet_LIB_DIRS_RELWITHDEBINFO}}
                                    ${{Bullet_LIB_DIRS_MINSIZEREL}}
                                    ${{Bullet_LIB_DIRS_DEBUG}})
            set(BULLET_ROOT_DIR "${{CMAKE_CURRENT_LIST_DIR}}/../../..")
            set(BULLET_VERSION_STRING {self.version})
        """)
        save(self, module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "bullet")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            f"conan-official-{self.name}-variables.cmake")

    @property
    def _bullet_definitions(self):
        defines = []
        if self.options.double_precision:
            defines.append("BT_USE_DOUBLE_PRECISION")
        return defines

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Bullet")
        self.cpp_info.set_property("cmake_target_name", "Bullet::Bullet") # not official
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "bullet")
        libs = []
        if self.options.bullet3:
            libs.extend([
                "Bullet3OpenCL_clew", # depends on LinearMath Bullet3Dynamics (and libdl on Linux)
                "Bullet3Dynamics", # depends on Bullet3Collision
                "Bullet3Collision", # depends on Bullet3Geometry
                "Bullet3Geometry",
                "Bullet2FileLoader", # depends on Bullet3Common
            ])
        if self.options.extras:
            libs.extend([
                "BulletRobotics", # depends on BulletInverseDynamicsUtils BulletWorldImporter BulletFileLoader BulletSoftBody BulletDynamics BulletCollision BulletInverseDynamics LinearMath Bullet3Common
                "BulletInverseDynamicsUtils", # depends on BulletInverseDynamics BulletDynamics BulletCollision Bullet3Common LinearMath
                "BulletXmlWorldImporter", # depends on BulletWorldImporter BulletDynamics BulletCollision BulletFileLoader LinearMath
                "BulletWorldImporter", # depends on BulletDynamics BulletCollision BulletFileLoader LinearMath
                "BulletFileLoader", # depends on LinearMath
                "GIMPACTUtils", # depends on ConvexDecomposition BulletCollision
                "ConvexDecomposition", # depends on BulletCollision LinearMath
                "HACD",
            ])
        libs.extend([
            "BulletSoftBody", # depends on BulletDynamics
            "BulletDynamics", # depends on BulletCollision & LinearMath
            "BulletCollision", # depends on LinearMath
            "BulletInverseDynamics", # depends on Bullet3Common & LinearMath
            "LinearMath",
            "Bullet3Common",
        ])
        if self.settings.os == "Windows" and self.settings.build_type in ("Debug", "MinSizeRel", "RelWithDebInfo"):
            lib_suffix = "RelWithDebugInfo" if self.settings.build_type == "RelWithDebInfo" else self.settings.build_type
            libs = [lib + "_{}".format(lib_suffix) for lib in libs]

        self.cpp_info.libs = libs
        self.cpp_info.includedirs = ["include", os.path.join("include", "bullet")]
        if self.options.extras:
            self.cpp_info.includedirs.append(os.path.join("include", "bullet_robotics"))
        self.cpp_info.defines = self._bullet_definitions
        if self.options.bt2_thread_locks and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Bullet"
        self.cpp_info.names["cmake_find_package_multi"] = "Bullet"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "bullet"
