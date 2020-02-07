#include <tinyxml2.h>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <ctime>

int main()
{
	static const char* xml =
		"<?xml version=\"1.0\"?>"
		"<!DOCTYPE PLAY SYSTEM \"play.dtd\">"
		"<PLAY>"
		"<TITLE>A Midsummer Night's Dream</TITLE>"
		"</PLAY>";

	tinyxml2::XMLDocument doc;
	doc.Parse( xml );

	return doc.ErrorID();
}
