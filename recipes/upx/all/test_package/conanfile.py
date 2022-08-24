from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_ext = ".exe" if self.settings.os == "Windows" else ""
            bin_path = os.path.join("bin", f"test_package{bin_ext}")

            upx_bin = self.deps_user_info["upx"].upx
            self.run(f"{upx_bin} --help", run_environment=True)

            original_size = os.stat(bin_path).st_size

            self.run(f"{upx_bin} {bin_path}", run_environment=True)

            packed_size = os.stat(bin_path).st_size

            # Run the packed executable to see whether it still works
            self.run(bin_path, run_environment=True)

            self.output.info(f"File: {bin_path}")
            self.output.info(f"Original size: {original_size:>9}")
            self.output.info(f"Packed size:   {packed_size:>9}")
            self.output.info(f"               ---------")
            self.output.info(f"Size diff:     {original_size-packed_size:>9}")
