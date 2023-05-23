from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class FlecsConan(ConanFile):
    name = "flecs"
    description = "A fast entity component system (ECS) for C & C++"
    license = "MIT"
    topics = ("gamedev", "cpp", "data-oriented-design", "c99",
              "game-development", "ecs", "entity-component-system",
              "cpp11", "ecs-framework")
    homepage = "https://github.com/SanderMertens/flecs"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "3.0.1":
            tc.variables["FLECS_STATIC_LIBS"] = not self.options.shared
            tc.variables["FLECS_SHARED_LIBS"] = self.options.shared
            tc.variables["FLECS_DEVELOPER_WARNINGS"] = False
        else:
            tc.variables["FLECS_STATIC"] = not self.options.shared
            tc.variables["FLECS_SHARED"] = self.options.shared
        tc.variables["FLECS_PIC"] = self.options.get_safe("fPIC", True)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        suffix = "" if self.options.shared else "_static"
        self.cpp_info.set_property("cmake_file_name", "flecs")
        self.cpp_info.set_property("cmake_target_name", f"flecs::flecs{suffix}")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_flecs"].libs = [f"flecs{suffix}"]
        if not self.options.shared:
            self.cpp_info.components["_flecs"].defines.append("flecs_STATIC")
        if Version(self.version) >= "3.0.0":
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["_flecs"].system_libs.append("pthread")
            elif self.settings.os == "Windows":
                self.cpp_info.components["_flecs"].system_libs.extend(["wsock32", "ws2_32"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "flecs"
        self.cpp_info.names["cmake_find_package_multi"] = "flecs"
        self.cpp_info.components["_flecs"].names["cmake_find_package"] = f"flecs{suffix}"
        self.cpp_info.components["_flecs"].names["cmake_find_package_multi"] = f"flecs{suffix}"
        self.cpp_info.components["_flecs"].set_property("cmake_target_name", f"flecs::flecs{suffix}")
