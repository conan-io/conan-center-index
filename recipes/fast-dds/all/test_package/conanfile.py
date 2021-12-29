import subprocess
from conans import ConanFile, CMake, tools
import os
from subprocess import Popen
import platform

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_sub_cmd = os.path.join("bin", "test_sub")
            bin_pub_cmd = os.path.join("bin", "test_pub")
            if platform.system() == "Darwin":
                # on Macos check just if able to execute
                command = "{0} &".format(bin_pub_cmd)
                self.run(command,run_environment=True)
            else:
                # Popen must be used to detect blocking process
                sub_process = Popen([bin_sub_cmd],stdout=subprocess.PIPE) 
                pub_process = Popen([bin_pub_cmd],stdout=subprocess.PIPE)
                sub_process.wait(30)
                pub_process.wait(30)
                msg_send = 'Message: HelloWorld with index: 5 SENT' in str(pub_process.stdout.read())
                msg_received = 'HelloWorld 5 RECEIVED' in str(sub_process.stdout.read())
                assert msg_send
                assert msg_received
