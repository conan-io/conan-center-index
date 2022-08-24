from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            mpiexec = os.path.join(os.environ['MPI_BIN'], 'mpiexec')
            command = '%s -mca plm_rsh_agent yes -np 2 %s' % (mpiexec, os.path.join("bin", "test_package"))
            self.run(command, run_environment=True)
