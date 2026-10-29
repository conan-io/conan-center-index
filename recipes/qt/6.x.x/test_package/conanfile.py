import os
import textwrap

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chmod, copy, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str, run=can_run(self))

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27]") # needed for `CMAKE_AUTO{tool}_EXECUTABLE` variables
        if not can_run(self):
            self.tool_requires(self.tested_reference_str)

    def generate(self):
        path = self.dependencies["qt"].package_folder.replace("\\", "/")
        save(self, "qt.conf", f"""[Paths]
Prefix = {path}""")

        tc = CMakeToolchain(self)
        if 'qt' in self.dependencies.build:
            qt_tools_rootdir = self.conf.get("user.qt:tools_directory", None)
            for tool in ["moc", "rcc", "uic"]:
                tc.cache_variables[f"CMAKE_AUTO{tool.upper()}_EXECUTABLE"] = os.path.join(qt_tools_rootdir, f"{tool}.exe" if self.settings_build.os == "Windows" else tool)
        else:
            bindir = "bin" if self.settings.os == "Windows" else "libexec"
            qt_tools_rootdir = os.path.join(self.dependencies["qt"].package_folder, bindir)
            is_windows = self.settings.os == "Windows"
            if is_windows:
                exe_ext, wrapper_ext, conanrun_name = ".exe", ".bat", "conanrun.bat"
                template = textwrap.dedent("""\
                    @echo off
                    call "{conanrun_script}"
                    "{real_tool}" %*
                    exit /b %ERRORLEVEL%
                    """)
            else:
                exe_ext, wrapper_ext, conanrun_name = "", "", "conanrun.sh"
                template = textwrap.dedent("""\
                    #!/bin/bash
                    source "{conanrun_script}"
                    exec "{real_tool}" "$@"
                    """)

            for tool in ["moc", "rcc", "uic"]:
                real_tool = os.path.join(qt_tools_rootdir, f"{tool}{exe_ext}")
                wrapper_path = os.path.join(self.generators_folder, f"{tool}{wrapper_ext}")
                conanrun_script = os.path.join(self.generators_folder, conanrun_name)
                save(self, wrapper_path, template.format(conanrun_script=conanrun_script, real_tool=real_tool))
                if not is_windows:
                    chmod(self, wrapper_path, execute=True)
                tc.cache_variables[f"CMAKE_AUTO{tool.upper()}_EXECUTABLE"] = wrapper_path
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            copy(self, "qt.conf", src=self.generators_folder, dst=os.path.join(self.cpp.build.bindirs[0]))
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
            # Related to https://github.com/conan-io/conan-center-index/issues/20574
            if self.settings.os == "Macos":
                bin_macos_path = os.path.join(self.cpp.build.bindirs[0], "test_macos_bundle.app", "Contents", "MacOS", "test_macos_bundle")
                self.run(bin_macos_path, env="conanrun")

        # Check that the directory exposed in the configuration exists and includes moc
        qt_tools_dir = self.dependencies.host["qt"].conf_info.get("user.qt:tools_directory")
        assert os.path.isdir(qt_tools_dir)
        moc = os.path.join(qt_tools_dir, "moc.exe" if self.settings.os == "Windows" else "moc")
        assert os.path.exists(moc)
