from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class CppLibP2P(ConanFile):
    name = "cpp-libp2p"
    description = "C++17 implementation of libp2p, a modular and extensible networking stack which solves many challenges of peer-to-peer applications."
    license = "MIT", "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libp2p/cpp-libp2p"
    topics = ("peer-to-peer", "distributed", "networking", "c++17")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # listed in cmake/dependencies.cmake
        self.requires("boost/1.81.0")
        self.requires("ms-gsl/4.0.0")
        self.requires("openssl/1.1.1t")
        self.requires("protobuf/3.21.9")
        self.requires("c-ares/1.19.0")
        self.requires("fmt/9.1.0")
        self.requires("yaml-cpp/0.7.0")
        # self.requires("soralog/???")  # in reality it uses fork: https://github.com/primihub/soralog
        self.requires("tsl-hat-trie/0.6.0")
        self.requires("di/1.2.0")  # in reality it uses fork: https://github.com/masterjedy/di
        # self.requires("sqlitemoderncpp/???")  # in reality it uses fork: https://github.com/soramitsu/libp2p-sqlite-modern-cpp

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TESTING"] = False
        tc.variables["EXAMPLES"] = False
        tc.variables["CLANG_FORMAT"] = False
        # cpp-libp2p uses the Hunter package manager, but we want to use dependencies provided by Conan
        tc.variables["HUNTER_ENABLED"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE-*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        libs_and_deps = [
            # src/CMakeLists.txt
            ("p2p", ["p2p_default_host", "p2p_default_network"]),

            # src/basic/CMakeLists.txt
            ("p2p_varint_reader", ["p2p_uvarint"]),
            ("p2p_varint_prefix_reader", ["p2p_logger"]),
            ("p2p_message_read_writer_error", ["Boost::boost"]),
            ("p2p_message_read_writer", ["p2p_message_read_writer_error", "p2p_varint_reader"]),
            ("p2p_protobuf_message_read_writer", ["p2p_message_read_writer"]),
            ("p2p_read_buffer", ["p2p_logger"]),
            ("p2p_write_queue", ["p2p_logger"]),
            ("p2p_basic_scheduler", ["p2p_logger"]),
            ("p2p_asio_scheduler_backend", ["p2p_basic_scheduler"]),
            ("p2p_manual_scheduler_backend", ["p2p_basic_scheduler"]),

            # src/common/CMakeLists.txt
            ("p2p_hexutil", ["Boost::boost"]),
            ("p2p_byteutil", ["Boost::boost"]),
            ("p2p_literals", ["p2p_peer_id", "p2p_multihash",
             "p2p_multiaddress", "p2p_hexutil"]),

            # src/connection/CMakeLists.txt
            ("p2p_connection_error", ["p2p_logger"]),
            ("p2p_loopback_stream", ["p2p_connection_error", "p2p_peer_id"]),

            # src/crypto/CMakeLists.txt
            ("p2p_crypto_error", ["Boost::boost"]),
            ("p2p_crypto_key", ["Boost::boost"]),
            ("p2p_crypto_common", ["p2p_crypto_error"]),
            # src/crypto/aes_provider/CMakeLists.txt
            ("p2p_aes_provider", ["p2p_crypto_error", "OpenSSL::Crypto"]),
            # src/crypto/chachapoly/CMakeLists.txt
            ("p2p_chachapoly_provider", ["p2p_crypto_error", "p2p_byteutil", "p2p_logger", "OpenSSL::Crypto"]),
            # src/crypto/crypto_provider/CMakeLists.txt
            ("p2p_crypto_provider", ["p2p_aes_provider", "p2p_crypto_error", "p2p_ecdsa_provider", "p2p_ed25519_provider", "p2p_hmac_provider",
             "p2p_rsa_provider", "p2p_random_generator", "p2p_secp256k1_provider", "OpenSSL::Crypto", "Boost::filesystem"]),
            # src/crypto/ecdsa_provider/CMakeLists.txt
            ("p2p_ecdsa_provider", ["p2p_crypto_error", "p2p_crypto_common", "p2p_sha", "OpenSSL::Crypto"]),
            # src/crypto/ed25519_provider/CMakeLists.txt
            ("p2p_ed25519_provider", ["p2p_crypto_error", "p2p_crypto_common", "p2p_sha", "OpenSSL::Crypto"]),
            # src/crypto/hmac_provider/CMakeLists.txt
            ("p2p_hmac_provider", ["p2p_crypto_error", "OpenSSL::Crypto"]),
            # src/crypto/key_marshaller/CMakeLists.txt
            ("p2p_key_marshaller", ["p2p_crypto_error", "p2p_crypto_key", "p2p_keys_proto"]),
            # src/crypto/key_validator/CMakeLists.txt
            ("p2p_key_validator", ["p2p_crypto_provider", "p2p_crypto_error", "OpenSSL::Crypto"]),
            # src/crypto/protobuf/CMakeLists.txt
            ("p2p_keys_proto", []),
            # src/crypto/random_generator/CMakeLists.txt
            ("p2p_random_generator", ["Boost::random"]),
            # src/crypto/rsa_provider/CMakeLists.txt
            ("p2p_rsa_provider", ["p2p_sha", "p2p_crypto_error", "OpenSSL::Crypto"]),
            # src/crypto/secp256k1_provider/CMakeLists.txt
            ("p2p_secp256k1_provider", ["p2p_sha", "p2p_crypto_error", "p2p_crypto_common", "OpenSSL::Crypto"])
            # master/src/crypto/sha/CMakeLists.txt
            ("p2p_sha", ["p2p_crypto_error", "OpenSSL::SSL", "OpenSSL::Crypto"]),
            # src/crypto/x25519_provider/CMakeLists.txt
            ("p2p_x25519_provider", ["p2p_crypto_error", "p2p_crypto_common", "OpenSSL::Crypto"]),

            # src/host/CMakeLists.txt
            ("p2p_default_host", ["p2p_basic_host", "p2p_inmem_key_repository",
             "p2p_peer_repository", "p2p_inmem_address_repository", "p2p_inmem_protocol_repository"]),
            # src/host/basic_host/CMakeLists.txt
            ("p2p_basic_host", ["Boost::boost", "p2p_multiaddress"]),

            # src/layer/websocket/CMakeLists.txt
            ("p2p_websocket", ["p2p_websocket_connection", "Boost::boost"]),
            ("p2p_websocket_connection", ["Boost::boost", "p2p_byteutil",
             "p2p_read_buffer", "p2p_write_queue", "p2p_connection_error", "p2p_sha"]),

            # src/log/CMakeLists.txt
            ("p2p_logger", ["soralog::soralog", "soralog::fallback_configurator", "soralog::configurator_yaml"]),

            # src/multi/CMakeLists.txt
            ("p2p_uvarint", ["Boost::boost", "p2p_hexutil", "p2p_logger"]),
            ("p2p_multihash", ["p2p_hexutil", "p2p_varint_prefix_reader", "Boost::boost"]),
            ("p2p_multiaddress", ["p2p_converters", "Boost::boost"]),
            ("p2p_cid", ["p2p_multihash", "p2p_sha", "p2p_uvarint", "p2p_multibase_codec"]),
            # src/multi/converters/CMakeLists.txt
            ("p2p_converters", ["Boost::boost", "p2p_hexutil", "p2p_byteutil", "p2p_uvarint", "p2p_multibase_codec"]),
            # src/multi/multibase_codec/CMakeLists.txt
            ("p2p_multibase_codec", ["p2p_hexutil", "Boost::boost"]),

            # src/muxer/mplex/CMakeLists.txt
            ("p2p_mplex", ["p2p_mplexed_connection"]),
            ("p2p_mplexed_connection", ["p2p_logger", "p2p_uvarint", "p2p_varint_reader", "p2p_connection_error"]),
            # src/muxer/yamux/CMakeLists.txt
            ("p2p_yamux", ["p2p_yamuxed_connection"]),
            ("p2p_yamuxed_connection", ["Boost::boost", "p2p_byteutil", "p2p_peer_id", "p2p_read_buffer", "p2p_write_queue", "p2p_connection_error"]),

            # src/network/CMakeLists.txt
            ("p2p_default_network", ["p2p_network", "p2p_tcp", "p2p_yamux", "p2p_mplex", "p2p_plaintext", "p2p_secio", "p2p_noise", "p2p_tls", "p2p_websocket", "p2p_connection_manager", "p2p_transport_manager", "p2p_listener_manager",
             "p2p_identity_manager", "p2p_dialer", "p2p_router", "p2p_multiselect", "p2p_random_generator", "p2p_crypto_provider", "p2p_key_validator", "p2p_key_marshaller", "p2p_basic_scheduler", "p2p_asio_scheduler_backend"]),
            # src/network/impl/CMakeLists.txt
            ("p2p_router", ["Boost::boost", "tsl::tsl_hat_trie", "p2p_peer_id"]),
            ("p2p_listener_manager", ["Boost::boost", "p2p_multiaddress", "p2p_peer_id", "p2p_logger"]),
            ("p2p_dialer", ["Boost::boost", "p2p_multiaddress", "p2p_multiselect", "p2p_peer_id", "p2p_logger"]),
            ("p2p_network", ["Boost::boost"]),
            ("p2p_transport_manager", ["p2p_multiaddress"]),
            ("p2p_connection_manager", ["Boost::boost"]),
            ("p2p_dnsaddr_resolver", ["Boost::boost", "p2p_cares"]),
            # src/network/cares/CMakeLists.txt
            ("p2p_cares", ["c-ares::cares", "pthread"]),

            # src/peer/CMakeLists.txt
            ("p2p_address_repository", ["Boost::boost"]),
            ("p2p_peer_errors", ["Boost::boost"]),
            ("p2p_peer_id", ["Boost::boost", "p2p_multihash", "p2p_multibase_codec", "p2p_sha"]),
            ("p2p_peer_address", ["Boost::boost", "p2p_multiaddress", "p2p_multihash", "p2p_multibase_codec", "p2p_peer_id"]),
            # src/peer/address_repository/CMakeLists.txt
            ("p2p_inmem_address_repository", ["p2p_address_repository", "p2p_multihash", "p2p_multiaddress", "p2p_peer_errors", "p2p_peer_id", "p2p_dnsaddr_resolver"]),
            # src/peer/impl/CMakeLists.txt
            ("p2p_identity_manager", ["p2p_peer_id"]),
            ("p2p_peer_repository", ["p2p_address_repository", "p2p_peer_id"]),
            # src/peer/key_repository/CMakeLists.txt
            ("p2p_inmem_key_repository", ["p2p_peer_errors", "p2p_multihash", "p2p_crypto_key", "p2p_peer_id"]),
            # src/peer/protocol_repository/CMakeLists.txt
            ("p2p_inmem_protocol_repository", ["Boost::boost", "p2p_peer_errors", "p2p_multihash", "p2p_peer_id"]),


            # src/protocol/echo/CMakeLists.txt
            ("p2p_protocol_echo", ["Boost::boost", "p2p_logger"]),
            # src/protocol/gossip/impl/CMakeLists.txt
            ("p2p_gossip", ["Boost::boost", "p2p_byteutil", "p2p_multiaddress", "p2p_varint_reader", "p2p_peer_id", "p2p_cid", "p2p_gossip_proto"]),
            # src/protocol/gossip/protobuf/CMakeLists.txt
            ("p2p_gossip_proto", []),
            # src/protocol/identify/CMakeLists.txt
            ("p2p_identify", ["p2p", "p2p_identify_proto", "p2p_protobuf_message_read_writer", "p2p_logger"]),
            ("p2p_identify_proto", []),
            # src/protocol/kademlia/CMakeLists.txt
            ("p2p_kademlia_message", ["p2p_cid", "p2p_kademlia_proto", "p2p_multiaddress", "p2p_peer_id"]),
            ("p2p_kademlia_error", ["Boost::boost"]),
            # src/protocol/kademlia/impl/CMakeLists.txt
            ("p2p_kademlia", ["p2p_basic_scheduler", "p2p_byteutil", "p2p_kademlia_message", "p2p_kademlia_error"]),
            # src/protocol/kademlia/protobuf/CMakeLists.txt
            ("p2p_kademlia_proto", []),
            # src/protocol/ping/CMakeLists.txt
            ("p2p_ping", ["Boost::boost"]),

            # src/protocol_muxer/CMakeLists.txt
            ("p2p_multiselect", ["p2p_read_buffer", "p2p_varint_prefix_reader", "p2p_logger", "p2p_hexutil"]),

            # src/security/CMakeLists.txt
            ("p2p_security_error", ["Boost::boost"]),
            # src/security/noise/CMakeLists.txt
            ("p2p_noise", ["Boost::boost", "p2p_noise_handshake_message_marshaller", "p2p_x25519_provider", "p2p_hmac_provider", "p2p_chachapoly_provider", "p2p_hexutil"]),
            ("p2p_noise_handshake_message_marshaller", ["Boost::boost", "p2p_noise_proto", "p2p_key_marshaller"]),
            # src/security/noise/protobuf/CMakeLists.txt
            ("p2p_noise_proto", []),
            # src/security/plaintext/CMakeLists.txt
            ("p2p_plaintext", ["Boost::boost", "p2p_crypto_error", "p2p_logger", "p2p_plaintext_exchange_message_marshaller", "p2p_protobuf_message_read_writer", "p2p_security_error"]),
            ("p2p_plaintext_exchange_message_marshaller", ["Boost::boost", "p2p_plaintext_proto", "p2p_key_marshaller"]),
            # src/security/plaintext/protobuf/CMakeLists.txt
            ("p2p_plaintext_proto", ["p2p_keys_proto"]),
            # src/security/secio/CMakeLists.txt
            ("p2p_secio", ["Boost::boost", "p2p_secio_propose_message_marshaller", "p2p_secio_exchange_message_marshaller", "p2p_secio_proto", "p2p_protobuf_message_read_writer", "p2p_logger", "p2p_crypto_error", "p2p_crypto_provider", "p2p_sha"]),
            ("p2p_secio_propose_message_marshaller", ["Boost::boost", "p2p_secio_proto", "p2p_message_read_writer"]),
            ("p2p_secio_exchange_message_marshaller", ["Boost::boost", "p2p_secio_proto", "p2p_message_read_writer"]),
            # src/security/secio/protobuf/CMakeLists.txt
            ("p2p_secio_proto", []),
            # src/security/tls/CMakeLists.txt
            ("p2p_tls", ["Boost::boost", "p2p_crypto_error", "p2p_logger", "p2p_security_error"]),

            # src/storage/CMakeLists.txt
            ("p2p_sqlite", ["SQLiteModernCpp::SQLiteModernCpp", "p2p_logger"]),

            # src/transport/impl/CMakeLists.txt
            ("p2p_transport_parser", ["Boost::boost", "p2p_multiaddress"]),
            ("p2p_upgrader", ["Boost::boost"]),
            ("p2p_upgrader_session", ["Boost::boost", "p2p_upgrader"]),
            # src/transport/tcp/CMakeLists.txt
            ("p2p_tcp_connection", ["Boost::boost", "p2p_multiaddress", "p2p_upgrader_session", "p2p_logger", "p2p_connection_error"]),
            ("p2p_tcp_listener", ["p2p_tcp_connection", "p2p_upgrader_session"]),
            ("p2p_tcp", ["p2p_tcp_connection", "p2p_tcp_listener"]),
        ]

        self.cpp_info.libs = ["p2p"]
        self.cpp_info.set_property("cmake_file_name", "libp2p")
        self.cpp_info.set_property("cmake_target_name", "p2p::p2p")
        self.cpp_info.requires = ["p2p_default_host", "p2p_default_network"]

        for name, requires in libs_and_deps[:1]:
            self.cpp_info.components[name].libs = [name]
            self.cpp_info.components[name].requires = requires
            self.cpp_info.components[name].set_property("cmake_target_name", f"p2p::{name}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libp2p"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libp2p"
        self.cpp_info.names["cmake_find_package"] = "libp2p"
        self.cpp_info.names["cmake_find_package_multi"] = "libp2p"
