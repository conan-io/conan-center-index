#include <iostream>
#include <fstream>
#include <FlexLexer.h>

// NOTE: this program is not meant to be run, only compiled and linked when cross-building

// Minimal usage: define all virtual functions required to link
yyFlexLexer::yyFlexLexer( std::istream& arg_yyin, std::ostream& arg_yyout ):
	yyin(arg_yyin.rdbuf()),
	yyout(arg_yyout.rdbuf())
{
	;
}

yyFlexLexer::~yyFlexLexer() { ; }

int yyFlexLexer::LexerInput( char* buf, int max_size ) {return 0;}
void yyFlexLexer::LexerOutput( const char* buf, int size ){;}
void yyFlexLexer::LexerError( const char* msg ){;}
int yyFlexLexer::yylex(){return 0;}
void yyFlexLexer::switch_streams( std::istream& new_in, std::ostream& new_out){;}
void yyFlexLexer::switch_streams( std::istream* new_in, std::ostream* new_out){;}
int yyFlexLexer::yywrap(){return 0;}
void yyFlexLexer::yy_switch_to_buffer( yy_buffer_state* new_buffer) {;}
yy_buffer_state* yyFlexLexer::yy_create_buffer( std::istream* s, int size) { return nullptr; }
yy_buffer_state* yyFlexLexer::yy_create_buffer( std::istream& s, int size ){ return nullptr; }
void yyFlexLexer::yy_delete_buffer( yy_buffer_state* b ){;}
void yyFlexLexer::yyrestart( std::istream* s ){;}
void yyFlexLexer::yyrestart( std::istream& s ){;}

int main(int argc, const char *argv[]) {
    // NOTE: this code is intented to test compiling and linking when cross-building,
    //       it is not expected to run or work at runtime.
    std::ifstream ifs("foobar");
	FlexLexer *lexer = new yyFlexLexer(ifs, std::cout);
	int result = lexer->yylex();
	return 0;
}