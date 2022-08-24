import os
import subprocess
from six import StringIO
from conans import ConanFile, CMake, tools

class NmosCppTestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    # use cmake_find_package_multi because the project installs a config-file package
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            with open("registry-config.json", "w") as config:
                config.write('{"http_port": 10000, "domain": "local.", "pri": 51967}')
            with open("node-config.json", "w") as config:
                config.write('{"http_port": 20000, "domain": "local.", "highest_pri": 51967, "lowest_pri": 51967}')

            # start up the installed nmos-cpp-registry to check it works
            registry = subprocess.Popen(["nmos-cpp-registry", "registry-config.json"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        universal_newlines=True)

            # run the test_package node which should have time to register and then exit
            node_out = StringIO()
            try:
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path + " node-config.json", run_environment=True, output=node_out)
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
