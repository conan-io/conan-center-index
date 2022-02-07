from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

conan_minimum_required = ">=1.43.0"


class BehaviorTreeCPPConan(ConanFile):
    name = "behaviortree.cpp"
    license = "MIT"
    homepage = "https://github.com/BehaviorTree/BehaviorTree.CPP"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("ai", "robotics", "games", "coordination")
    description = "This C++ library provides a framework to create BehaviorTrees"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cppstd_required(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "12",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("cppzmq/4.8.1")
        self.requires("ncurses/6.3")
        self.requires("zeromq/4.3.4")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("BehaviorTree.CPP can not be built as shared on Windows.")
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cppstd_required)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("BehaviorTree.CPP requires C++{}. Your compiler is unknown. Assuming it supports C++14."
                             .format(self._minimum_cppstd_required))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("BehaviorTree.CPP requires C++{}, which your compiler does not support."
                                            .format(self._minimum_cppstd_required))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_UNIT_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "BehaviorTreeV3"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "BehaviorTreeV3")
        self.cpp_info.set_property("cmake_target_name", "BT::behaviortree_cpp_v3")
        postfix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["behaviortree_cpp_v3"].libs = ["behaviortree_cpp_v3" + postfix]
        self.cpp_info.components["behaviortree_cpp_v3"].requires = ["zeromq::zeromq", "cppzmq::cppzmq", "boost::coroutine", "ncurses::ncurses"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["behaviortree_cpp_v3"].system_libs.append("pthread")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "BehaviorTreeV3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "BehaviorTreeV3"
        self.cpp_info.names["cmake_find_package"] = "BT"
        self.cpp_info.names["cmake_find_package_multi"] = "BT"
        self.cpp_info.components["behaviortree_cpp_v3"].names["cmake_find_package"] = "behaviortree_cpp_v3"
        self.cpp_info.components["behaviortree_cpp_v3"].names["cmake_find_package_multi"] = "behaviortree_cpp_v3"
        self.cpp_info.components["behaviortree_cpp_v3"].set_property("cmake_target_name", "BT::behaviortree_cpp_v3")
