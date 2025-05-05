/*
 **************************************************************
 *         C++ Mathematical Expression Toolkit Library        *
 *                                                            *
 * Exprtk Test Package                                        *
 * Author: Arash Partow (1999-2022)                           *
 * URL: https://www.partow.net/programming/exprtk/index.html  *
 *                                                            *
 * Copyright notice:                                          *
 * Free use of the Mathematical Expression Toolkit Library is *
 * permitted under the guidelines and in accordance with the  *
 * most current version of the MIT License.                   *
 * http://www.opensource.org/licenses/MIT                     *
 *                                                            *
 **************************************************************
*/


#include <cstdio>
#include <string>

#include <exprtk.hpp>


template <typename T>
void test_function()
{
   typedef exprtk::symbol_table<T>    symbol_table_t;
   typedef exprtk::expression<T>      expression_t;
   typedef exprtk::parser<T>          parser_t;
   typedef exprtk::parser_error::type error_t;

   symbol_table_t symbol_table;
   expression_t   expression;
   parser_t       parser;

   T x = 1;
   T y = 2;

   const std::string expression_string = "x * y + 3";

   symbol_table.add_variable("x",x);
   symbol_table.add_variable("y",y);

   expression.register_symbol_table(symbol_table);

   if (!parser.compile(expression_string,expression))
   {
      printf("Error: %s\tExpression: %s\n",
             parser.error().c_str(),
             expression_string.c_str());

      for (std::size_t i = 0; i < parser.error_count(); ++i)
      {
         const error_t error = parser.get_error(i);

         printf("Error: %02d Position: %02d "
                "Type: [%s] "
                "Message: %s "
                "Expression: %s\n",
                static_cast<int>(i),
                static_cast<int>(error.token.position),
                exprtk::parser_error::to_str(error.mode).c_str(),
                error.diagnostic.c_str(),
                expression_string.c_str());
      }

      return;
   }

   expression.value();
}

int main()
{
   test_function<double>();
   return 0;
}
