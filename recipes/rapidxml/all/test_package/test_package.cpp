#include <rapidxml/rapidxml.hpp>
#include <rapidxml/rapidxml_print.hpp>

#include <cstdio>
#include <iostream>
#include <fstream>
#include <vector>

int main(int argc, char **argv)
{
  if (argc < 2) {
    std::cerr << "Need at least one argument\n";
    return 1;
  }

  std::cout << "Parsing my beer journal..." << std::endl;
  rapidxml::xml_document<> doc;
  rapidxml::xml_node<> * root_node;
  // Read the xml file into a vector
  std::ifstream theFile(argv[1]);
  std::vector<char> buffer((std::istreambuf_iterator<char>(theFile)), std::istreambuf_iterator<char>());
  buffer.push_back('\0');
  // Parse the buffer using the xml file parsing library into doc
  doc.parse<0>(&buffer[0]);
  // Find our root node
  root_node = doc.first_node("MyBeerJournal");
  // Iterate over the brewerys
  for (rapidxml::xml_node<> * brewery_node = root_node->first_node("Brewery"); brewery_node; brewery_node = brewery_node->next_sibling())
  {
    printf("I have visited %s in %s. ",
           brewery_node->first_attribute("name")->value(),
           brewery_node->first_attribute("location")->value());
    // Interate over the beers
    for(rapidxml::xml_node<> * beer_node = brewery_node->first_node("Beer"); beer_node; beer_node = beer_node->next_sibling())
    {
      printf("On %s, I tried their %s which is a %s. ",
             beer_node->first_attribute("dateSampled")->value(),
             beer_node->first_attribute("name")->value(),
             beer_node->first_attribute("description")->value());
      printf("I gave it the following review: %s", beer_node->value());
    }
    std::cout << std::endl;
  }

  std::cout << "Original xml document:" << std::endl;
  std::cout << doc;

  return 0;
}
