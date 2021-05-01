from conans import ConanFile, CMake, tools
import os
import subprocess
import re


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        if tools.cross_building(self.settings) and self.settings.os in ["iOS"]:
            return  # on iOS I do not even need to build, it will just give am a and error about unsigned binaries       
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings) and self.settings.os in ["Android", "iOS"]:
            return 

        if "arm" in self.settings.arch:
            self.test_arm()
        elif tools.cross_building(self.settings) and self.settings.os == "Windows":
            self.test_mingw_cross()
        elif not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

    def test_mingw_cross(self):
        bin_path = os.path.join("bin", "test_package.exe")
        output = subprocess.check_output(["file", bin_path]).decode()
        assert re.search(r"PE32.*executable.*Windows", output)

    def test_arm(self):
        file_ext = "so" if self.options["libcurl"].shared else "a"
        lib_path = os.path.join(self.deps_cpp_info["libcurl"].libdirs[0], "libcurl.%s" % file_ext)
        output = subprocess.check_output(["readelf", "-h", lib_path]).decode()

        if "armv8" in self.settings.arch:
            if self.settings.arch == "armv8_32":
                assert re.search(r"Machine:\s+ARM", output)
            else:
                assert re.search(r"Machine:\s+AArch64", output)
        else:
            assert re.search(r"Machine:\s+ARM", output)
