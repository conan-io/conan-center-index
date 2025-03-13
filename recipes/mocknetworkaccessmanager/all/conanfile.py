import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, save

required_conan_version = ">=2.0.9"


class MockNetworkAccessManagerConan(ConanFile):
    name = "mocknetworkaccessmanager"
    description = "Mocking network communication for Qt applications"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/julrich/MockNetworkAccessManager"
    topics = ("qt", "mock", "network", "QNetworkAccessManager", "unit test", "test")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_qt": [5, 6, "deprecated"],
    }
    default_options = {
        "fPIC": True,
        "with_qt": "deprecated",
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def package_id(self):
        del self.info.options.with_qt

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_qt == 5:
            self.requires("qt/[~5.15]", transitive_headers=True)
        else:
            self.requires("qt/[>=5.15 <7]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <4]")
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        replace_in_file(self, "CMakeLists.txt", "set( CMAKE_CXX_STANDARD 11 )", "")
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "doc", "CMakeLists.txt"), "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["FORCE_QT5"] = self.dependencies["qt"].ref.version.major == 5
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        # cmake.install() fails without the explicit target
        cmake.build(target="MockNetworkAccessManager")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["MockNetworkAccessManager"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtNetwork"]
        qt = self.dependencies["qt"]
        if qt.ref.version.major == 6 and qt.options.qt5compat:
            self.cpp_info.requires.append("qt::qtCore5Compat")
