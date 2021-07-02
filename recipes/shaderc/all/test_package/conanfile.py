import os

from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SHADERC_WITH_SPVC"] = self.options["shaderc"].spvc
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            # Test programs consuming shaderc lib
            bin_path_shaderc_c = os.path.join("bin", "test_package_shaderc_c")
            self.run(bin_path_shaderc_c, run_environment=True)
            bin_path_shaderc_cpp = os.path.join("bin", "test_package_shaderc_cpp")
            self.run(bin_path_shaderc_cpp, run_environment=True)
            # Test glslc executable
            in_glsl_name = os.path.join(self.source_folder, "test_package.vert")
            spv_name = "test_package.spv"
            self.run("glslc \"{0}\" -o {1}".format(in_glsl_name, spv_name), run_environment=True)

            if self.options["shaderc"].spvc:
                # Test programs consuming shaderc_spvc lib
                bin_path_spvc_c = os.path.join("bin", "test_package_spvc_c")
                self.run(bin_path_spvc_c, run_environment=True)
                bin_path_spvc_cpp = os.path.join("bin", "test_package_spvc_cpp")
                self.run(bin_path_spvc_cpp, run_environment=True)
