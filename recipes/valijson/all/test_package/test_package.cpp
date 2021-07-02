#include <rapidjson/document.h>

#include <valijson/adapters/rapidjson_adapter.hpp>
#include <valijson/utils/rapidjson_utils.hpp>
#include <valijson/schema.hpp>
#include <valijson/schema_parser.hpp>
#include <valijson/validator.hpp>

#include <iostream>
#include <stdexcept>

using valijson::Schema;
using valijson::SchemaParser;
using valijson::Validator;
using valijson::adapters::RapidJsonAdapter;

// To check successful compilation
#include <valijson/adapters/nlohmann_json_adapter.hpp>
#include <valijson/utils/nlohmann_json_utils.hpp>

#define PICOJSON_USE_INT64
#include <valijson/adapters/picojson_adapter.hpp>
#include <valijson/utils/picojson_utils.hpp>

#include <valijson/internal/optional.hpp>

void check_document(const Schema& mySchema, const char* filename, bool is_valid_expectation) {
    rapidjson::Document myTargetDoc;
    if (!valijson::utils::loadDocument(filename, myTargetDoc)) {
        throw std::runtime_error("Failed to load target document");
    }

    Validator validator;
    RapidJsonAdapter myTargetAdapter(myTargetDoc);
    if (validator.validate(mySchema, myTargetAdapter, NULL) != is_valid_expectation) {
        throw std::runtime_error("Validation failed.");
    }
}

int main(int argc, const char* argv[]) {
    if (argc != 4) {
        throw std::runtime_error("Expected: binary schema.json valid.json invalid.json");
    }
    // Load JSON document using RapidJSON with Valijson helper function
    rapidjson::Document mySchemaDoc;
    if (!valijson::utils::loadDocument(argv[1], mySchemaDoc)) {
        throw std::runtime_error("Failed to load schema document");
    }

    // Parse JSON schema content using valijson
    Schema mySchema;
    SchemaParser parser;
    RapidJsonAdapter mySchemaAdapter(mySchemaDoc);
    parser.populateSchema(mySchemaAdapter, mySchema);

    check_document(mySchema, argv[2], true);
    check_document(mySchema, argv[3], false);

    std::cout << "valijson successful run\n";

    return 0;
}
