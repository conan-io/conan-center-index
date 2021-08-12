from conans import CMake, ConanFile, tools
import textwrap
import os


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("make/4.3")

    @property
    def _supports_executables(self):
        return self.options["arm-toolchain"].target_os == "Linux"

    def build(self):
        arm_64bit = self.options["arm-toolchain"].target_arch == "armv8"

        if not tools.cross_building(self, skip_x64_x86=True):
            tools.save("toolchain.cmake", textwrap.dedent("""\
                set(CMAKE_SYSTEM_NAME {system_name})
                set(CMAKE_SYSTEM_PROCESSOR {system_processor})

                # Set these variables explicitly to enable the test, even when using conan 1 profile build
                set(CMAKE_C_COMPILER {cc})
                set(CMAKE_CXX_COMPILER {cxx})

                if(NOT {supports_executables})
                    set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
                endif()

                set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
                set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
                set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
            """).format(
                system_name=self.deps_user_info["arm-toolchain"].cmake_system_os,
                system_processor=self.deps_user_info["arm-toolchain"].target_gnu_arch,
                cc=self.deps_env_info["arm-toolchain"].CC,
                cxx=self.deps_env_info["arm-toolchain"].CXX,
                supports_executables=self._supports_executables,
            ))
            cmake = CMake(self)
            cmake.generator = "Unix Makefiles"
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(self.build_folder, "toolchain.cmake").replace("\\", "/")
            cmake.definitions["ARM_64BIT"] = arm_64bit
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            if self._supports_executables:
                assert os.path.isfile("test_package")
            else:
                assert os.path.isfile("libtest_package.a")
