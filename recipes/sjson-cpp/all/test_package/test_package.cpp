#include <sjson/parser.h>

using namespace sjson;

static Parser createParser(const char* c_str)
{
	return Parser(c_str, std::strlen(c_str));
}

int main()
{
    Parser parser = createParser("key = true");
    bool value = false;
    parser.read("key", value);

    return 0;
}
