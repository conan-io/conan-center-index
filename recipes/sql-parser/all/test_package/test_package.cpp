#include <string>
#include <iostream>

#include "hsql/SQLParser.h"

int main() {
    const std::string query = "SELECT * FROM students;";
    hsql::SQLParserResult result;
    hsql::SQLParser::parse(query, &result);

    if (result.isValid() && result.size() > 0) {
        const hsql::SQLStatement* statement = result.getStatement(0);

        if (statement->isType(hsql::kStmtSelect)) {
            const auto* select = static_cast<const hsql::SelectStatement*>(statement);

            std::cout << select->fromTable->getName() << '\n';
        }
    }
    return 0;
}
