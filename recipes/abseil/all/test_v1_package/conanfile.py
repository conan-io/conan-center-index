from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _skip_cpp17_build(self):
        # 20240116 added a hasher for std::filesystem::path, so absl/hash/internal/hash.h
        # includes <filesystem> if in C++17 mode. GCC 7 supported C++17, but notably
        # <filesystem> was added in GCC 8.
        return tools.Version(self.deps_cpp_info["abseil"].version) >= "20240116" \
            and self.settings.compiler == "gcc" \
            and int(tools.Version(self.settings.compiler.version).major) == 7

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CXX20_SUPPORTED"] = tools.Version(self.deps_cpp_info["abseil"].version) > "20210324.2"
        cmake.definitions["SKIP_CPP_17_BUILD"] = self._skip_cpp17_build
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(f"{bin_path} -s", run_environment=True)
            bin_global_path = os.path.join("bin", "test_package_global")
            self.run(f"{bin_global_path} -s", run_environment=True)
