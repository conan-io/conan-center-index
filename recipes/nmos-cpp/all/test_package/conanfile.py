from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os
import shutil
import subprocess
from six import StringIO


class NmosCppTestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with open("registry-config.json", "w", encoding="utf-8") as config:
                config.write('{"http_port": 10000, "domain": "local.", "pri": 51967}')
            with open("node-config.json", "w", encoding="utf-8") as config:
                config.write('{"http_port": 20000, "domain": "local.", "highest_pri": 51967, "lowest_pri": 51967}')

            # find and start up the installed nmos-cpp-registry to check it works
            registry_path = shutil.which("nmos-cpp-registry", path=os.pathsep.join(self.env["PATH"]))
            registry = subprocess.Popen([registry_path, "registry-config.json"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        universal_newlines=True)

            # run the test_package node which should have time to register and then exit
            node_out = StringIO()
            try:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
                self.run(bin_path + " node-config.json", env="conanrun", output=node_out)
            finally:
                registry.terminate()
            if "Adopting registered operation" not in node_out.getvalue():
                self.output.warn("test_package node failed to register with nmos-cpp-registry\n"
                                 "\n"
                                 "nmos-cpp-registry log:\n"
                                 "{}\n"
                                 "test_package log:\n"
                                 "{}"
                                 .format(registry.communicate()[0], node_out.getvalue()))
