#include "enjinsdk/GraphqlQueryRegistry.hpp"
#include "enjinsdk/models/AccessToken.hpp"
#include "enjinsdk/project/AuthProject.hpp"
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

using namespace enjin::sdk::graphql;
using namespace enjin::sdk::models;
using namespace enjin::sdk::project;

void test_model_deserialization();

void test_query_registry();

void test_request_serialization();

int main() {
    test_model_deserialization();
    test_query_registry();
    test_request_serialization();

    return 0;
}

void test_model_deserialization() {
    const std::string token = "xyz";
    const long expiration = 100L;

    std::stringstream json_stream;
    json_stream << R"({"accessToken":")" << token << R"(","expiresIn":)" << expiration << R"(})";
    const std::string json = json_stream.str();

    AccessToken access_token;
    access_token.deserialize(json);

    const std::optional <std::string>& token_opt = access_token.get_token();
    if (!token_opt.has_value()) {
        throw std::runtime_error(R"(Field "token" was not serialized)");
    }

    const std::optional<long>& expiration_opt = access_token.get_expires_in();
    if (!expiration_opt.has_value()) {
        throw std::runtime_error(R"(Field "expiresIn" was not serialized)");
    }

    std::cout << "AccessToken result:"
              << "\n* token: [" << token_opt.value() << "] (expected: [" << token << "])"
              << "\n* expiresIn: [" << expiration_opt.value() << "] (expected: [" << expiration << "])"
              << "\n" << std::endl;
}

void test_query_registry() {
    const GraphqlQueryRegistry registry;
    const AuthProject req;

    const std::string& req_namespace = req.get_namespace();
    const bool has_operation = registry.has_operation_for_name(req_namespace);

    if (!has_operation) {
        throw std::runtime_error("Could not find operation for namespace \"" + req_namespace + "\"");
    }

    std::cout << "GraphqlQueryRegistry result:"
              << "\n* Found operation for namespace \"" << req_namespace << "\""
              << "\n" << std::endl;
}

void test_request_serialization() {
    const std::string uuid = "TestUuid";
    const std::string secret = "TestSecret";

    AuthProject req = AuthProject().set_uuid(uuid).set_secret(secret);
    const std::string req_json = req.serialize();

    if (req_json.find(uuid) == std::string::npos) {
        throw std::runtime_error("Did not find UUID in serialized JSON");
    }

    if (req_json.find(secret) == std::string::npos) {
        throw std::runtime_error("Did not find secret in serialized JSON");
    }

    std::cout << "AuthProject result:"
              << "\n* Request JSON: " << req_json
              << "\n* Found UUID and secret in serialized JSON"
              << "\n" << std::endl;
}
