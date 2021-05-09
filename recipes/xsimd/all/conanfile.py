from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class XsimdConan(ConanFile):
    name = "xsimd"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xsimd"
    description = "C++ wrappers for SIMD intrinsics and parallelized, optimized mathematical functions (SSE, AVX, NEON, AVX512)"
    topics = ("conan", "simd-intrinsics", "vectorization", "simd")
    options = {"xtl_complex": [True, False]}
    default_options = {"xtl_complex": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.xtl_complex:
            self.requires("xtl/0.7.2")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include")
        )

    def package_info(self):
        if self.options.xtl_complex:
            self.cpp_info.defines = ["XSIMD_ENABLE_XTL_COMPLEX=1"]
