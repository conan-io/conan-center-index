/*
 * This file is part of flex.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * Neither the name of the University nor the names of its contributors
 * may be used to endorse or promote products derived from this software
 * without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE.
 */

%option C++ noyywrap

%{
int mylineno = 0;
%}

string	\"[^\n"]+\"

ws	[ \t]+

alpha	[A-Za-z]
dig	[0-9]
name	({alpha}|{dig}|\$)({alpha}|{dig}|\_|\.|\-|\/|\$)*
num1	[-+]?{dig}+\.?([eE][-+]?{dig}+)?
num2	[-+]?{dig}*\.{dig}+([eE][-+]?{dig}+)?
number	{num1}|{num2}

%%

{ws}	/* skip blanks and tabs */

"/*"		{
		int c;

		while((c = yyinput()) != 0)
			{
			if(c == '\n')
				++mylineno;

			else if(c == '*')
				{
				if((c = yyinput()) == '/')
					break;
				else
					unput(c);
				}
			}
		}

{number}	std::cout << "number " << YYText() << '\n';

\n		mylineno++;

{name}		std::cout << "name " << YYText() << '\n';

{string}	std::cout << "string " << YYText() << '\n';

%%

extern "C" {
    int yylex() {return 0;}
}

#include <fstream>

int main( int argc, const char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Need an argument\n");
        return 1;
    }
    std::ifstream ifs(argv[1]);
	FlexLexer *lexer = new yyFlexLexer(ifs, std::cout);
	while(lexer->yylex() != 0)
		;
	return 0;
}
