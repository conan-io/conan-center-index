from conans import CMake, ConanFile, tools
import textwrap
import os


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("make/4.3")

    def build(self):
        arm_64bit = self.options["arm-toolchain"].target_arch == "armv8"

        if not tools.cross_building(self, skip_x64_x86=True):
            tools.save("toolchain.cmake", textwrap.dedent("""\
                set(CMAKE_SYSTEM_NAME {system_name})
                set(CMAKE_SYSTEM_PROCESSOR {system_processor})

                # Set these variables explicitly to enable the test, even when using conan 1 profile build
                set(CMAKE_C_COMPILER {cc})
                set(CMAKE_CXX_COMPILER {cxx})
            """).format(
                system_name=self.deps_user_info["arm-toolchain"].cmake_system_os,
                system_processor=self.deps_user_info["arm-toolchain"].target_gnu_arch,
                cc=self.deps_env_info["arm-toolchain"].CC,
                cxx=self.deps_env_info["arm-toolchain"].CXX,
            ))
            cmake = CMake(self)
            cmake.generator = "Unix Makefiles"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(self.build_folder, "toolchain.cmake").replace("\\", "/")
            cmake.definitions["ARM_64BIT"] = arm_64bit
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            assert os.path.isfile("test_package")
