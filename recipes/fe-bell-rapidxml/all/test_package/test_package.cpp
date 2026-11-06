#include <rapidxml/rapidxml.hpp>
#include <rapidxml/rapidxml_print.hpp>

#include <cstdio>
#include <cstring>
#include <iostream>

int main() {
    char xml[] = "<MyBeerJournal>"
                 "<Brewery name=\"Test Brewery\" location=\"Test City\"/>"
                 "</MyBeerJournal>";

    rapidxml::xml_document<> doc;
    doc.parse<0>(xml);

    rapidxml::xml_node<>* root = doc.first_node("MyBeerJournal");
    for (rapidxml::xml_node<>* brewery = root->first_node("Brewery");
         brewery; brewery = brewery->next_sibling()) {
        printf("I have visited %s in %s.\n",
               brewery->first_attribute("name")->value(),
               brewery->first_attribute("location")->value());
    }

    return 0;
}
