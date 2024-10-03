from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout
from conan.tools.meson import Meson


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "PkgConfigDeps", "MesonToolchain", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("cpython/3.12.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    # Note: when building with CMake, the following is required:
    # def generate(self):
    #     VirtualRunEnv(self).generate()
    #     # Required for find_package(Python) to work with cpython/*:shared=True
    #     VirtualRunEnv(self).generate(scope="build")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def test(self):
        if can_run(self):
            self.run('python -c "import test_package; print(test_package.create_numpy_array())"',
                     env=["conanbuild", "conanrun"], cwd=self.build_folder)
