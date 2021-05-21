from conans import ConanFile, CMake


class JumpstartedSkeletonTest(ConanFile):
    settings = ()
    generators = 'cmake_find_package'

    build_requires = 'doxygen/[^1.8.0]'

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def test(self):
        cmake = CMake(self)
        cmake.build(target='docs')
