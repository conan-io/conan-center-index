from conan.tools.microsoft import msvc_runtime_flag
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


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
        "bullet3": False,
        "graphical_benchmark": False,
        "double_precision": False,
        "bt2_thread_locks": False,
        "soft_body_multi_body_dynamics_world": False,
        "network_support": False,
        "extras": False,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries on Visual Studio not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_BULLET3"] = self.options.bullet3
        cmake.definitions["INSTALL_LIBS"] = True
        cmake.definitions["USE_GRAPHICAL_BENCHMARK"] = self.options.graphical_benchmark
        cmake.definitions["USE_DOUBLE_PRECISION"] = self.options.double_precision
        cmake.definitions["BULLET2_USE_THREAD_LOCKS"] = self.options.bt2_thread_locks
        cmake.definitions["USE_SOFT_BODY_MULTI_BODY_DYNAMICS_WORLD"] = self.options.soft_body_multi_body_dynamics_world
        cmake.definitions["BUILD_ENET"] = self.options.network_support
        cmake.definitions["BUILD_CLSOCKET"] = self.options.network_support
        cmake.definitions["BUILD_CPU_DEMOS"] = False
        cmake.definitions["BUILD_OPENGL3_DEMOS"] = False
        cmake.definitions["BUILD_BULLET2_DEMOS"] = False
        cmake.definitions["BUILD_EXTRAS"] = self.options.extras
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        if self._is_msvc:
            cmake.definitions["USE_MSVC_RUNTIME_LIBRARY_DLL"] = "MD" in msvc_runtime_flag(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
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

        self.cpp_info.names["cmake_find_package"] = "Bullet"
        self.cpp_info.names["cmake_find_package_multi"] = "Bullet"
        self.cpp_info.names["pkg_config"] = "bullet"
        self.cpp_info.libs = libs
        self.cpp_info.includedirs = ["include", os.path.join("include", "bullet")]
        if self.options.extras:
            self.cpp_info.includedirs.append(os.path.join("include", "bullet_robotics"))
        if self.options.double_precision:
            self.cpp_info.defines.append("BT_USE_DOUBLE_PRECISION")
