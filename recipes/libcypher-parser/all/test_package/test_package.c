#include <cypher-parser.h>

int main()
{
  cypher_parse_result_t *result = cypher_parse("MATCH (a) RETURN a",
					       NULL,
					       NULL,
					       CYPHER_PARSE_ONLY_STATEMENTS);
    return 0;
}
