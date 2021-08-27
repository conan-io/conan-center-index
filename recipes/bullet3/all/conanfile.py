from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class Bullet3Conan(ConanFile):
    name = "bullet3"
    description = "Bullet Physics SDK: real-time collision detection and multi-physics simulation for VR, games, visual effects, robotics, machine learning etc."
    homepage = "https://github.com/bulletphysics/bullet3"
    topics = "conan", "bullet", "physics", "simulation", "robotics", "kinematics", "engine",
    license = "ZLIB"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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
        "extras": [True, False]
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
        "extras": False
    }

    _source_subfolder = "source_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries on Visual Studio not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("bullet3-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_BULLET3"] = self.options.bullet3
        self._cmake.definitions["INSTALL_LIBS"] = True
        self._cmake.definitions["USE_GRAPHICAL_BENCHMARK"] = self.options.graphical_benchmark
        self._cmake.definitions["USE_DOUBLE_PRECISION"] = self.options.double_precision
        self._cmake.definitions["BULLET2_USE_THREAD_LOCKS"] = self.options.bt2_thread_locks
        self._cmake.definitions["USE_SOFT_BODY_MULTI_BODY_DYNAMICS_WORLD"] = self.options.soft_body_multi_body_dynamics_world
        self._cmake.definitions["BUILD_ENET"] = self.options.network_support
        self._cmake.definitions["BUILD_CLSOCKET"] = self.options.network_support
        self._cmake.definitions["BUILD_CPU_DEMOS"] = False
        self._cmake.definitions["BUILD_OPENGL3_DEMOS"] = False
        self._cmake.definitions["BUILD_BULLET2_DEMOS"] = False
        self._cmake.definitions["BUILD_EXTRAS"] = self.options.extras
        self._cmake.definitions["BUILD_UNIT_TESTS"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["USE_MSVC_RUNTIME_LIBRARY_DLL"] = "MD" in self.settings.compiler.runtime
        self._cmake.configure()
        return self._cmake

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
            libs += [
                "Bullet2FileLoader",
                "Bullet3Collision",
                "Bullet3Dynamics",
                "Bullet3Geometry",
                "Bullet3OpenCL_clew",
            ]
        libs += [
            "BulletDynamics",
            "BulletCollision",
            "LinearMath",
            "BulletSoftBody",
            "Bullet3Common",
            "BulletInverseDynamics",
        ]
        if self.options.extras:
            libs += [   "BulletInverseDynamicsUtils",
                        "BulletRobotics",
                        "BulletFileLoader",
                        "BulletXmlWorldImporter",
                        "BulletWorldImporter",
                        "ConvexDecomposition",
                        "HACD",
                        "GIMPACTUtils"
                    ]
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
