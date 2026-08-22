%{
#include <iostream>
#include <string>
#include <map>
#include <cstdlib> //-- I need this for atoi
using namespace std;

int yylex();
int yyerror(const char *p) { cerr << "Error!" << endl; return 42; }
%}

%union {
  int val;
  char sym;
};
%token <val> NUM
%token <sym> OPA OPM LP RP STOP
%type  <val> exp term sfactor factor res

%%
run: res run | res    /* forces bison to process many stmts */

res: exp STOP         { cout << $1 << endl; }

exp: exp OPA term     { $$ = ($2 == '+' ? $1 + $3 : $1 - $3); }
| term                { $$ = $1; }

term: term OPM factor { $$ = ($2 == '*' ? $1 * $3 : $1 / $3); }
| sfactor             { $$ = $1; }

sfactor: OPA factor   { $$ = ($1 == '+' ? $2 : -$2); }
| factor              { $$ = $1; }

factor: NUM           { $$ = $1; }
| LP exp RP           { $$ = $2; }

%%
int main()
{
    yyparse();
    return 0;
}
