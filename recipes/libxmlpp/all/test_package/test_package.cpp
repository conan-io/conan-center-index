/*
 * Copyright (C) 2002 The libxml++ development team
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the Free
 * Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <libxml++/libxml++.h>
#include <libxml++/parsers/textreader.h>

#include <iostream>
#include <stdlib.h>

struct indent {
  int depth_;
  explicit indent(int depth): depth_(depth) {};
};

std::ostream & operator<<(std::ostream & o, indent const & in)
{
  for(int i = 0; i != in.depth_; ++i)
  {
    o << "  ";
  }
  return o;
}

int main(int argc, char** argv)
{
  if (argc == 1) {
    std::cerr << "Expected an xml file as a command line argument!\n";
    return EXIT_FAILURE;
  }

  try
  {
    xmlpp::TextReader reader(argv[1]);

    while(reader.read())
    {
      int depth = reader.get_depth();
      std::cout << indent(depth) << "--- node ---" << std::endl;
      std::cout << indent(depth) << "name: " << reader.get_name() << std::endl;
      std::cout << indent(depth) << "depth: " << reader.get_depth() << std::endl;

      if(reader.has_attributes())
      {
        std::cout << indent(depth) << "attributes: " << std::endl;
        reader.move_to_first_attribute();
        do
        {
          std::cout << indent(depth) << "  " << reader.get_name() << ": " << reader.get_value() << std::endl;
        } while(reader.move_to_next_attribute());
        reader.move_to_element();
      }
      else
      {
        std::cout << indent(depth) << "no attributes" << std::endl;
      }

      if(reader.has_value())
        std::cout << indent(depth) << "value: '" << reader.get_value() << "'" << std::endl;
      else
        std::cout << indent(depth) << "novalue" << std::endl;

    }
  }
  catch(const std::exception& e)
  {
    std::cerr << "Exception caught: " << e.what() << std::endl;
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}

