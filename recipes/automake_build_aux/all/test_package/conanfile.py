from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):

    def test(self):
        assert os.path.isfile(os.path.join(self.deps_cpp_info["automake_build_aux"].bin_paths[0], "compile"))
        assert os.path.isfile(os.path.join(self.deps_cpp_info["automake_build_aux"].bin_paths[0], "ar-lib"))

