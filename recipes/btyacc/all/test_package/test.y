%{
/* first section */
%}
/*
 * [test] btyacc
 * [test] cc
 * [test] input (())()(())
 * [test] input-fail (())(*)(())
 * [test] btyacc -DABC
 * [test] cc
 * [test] input (())(*)(())
 */
%%
%{
/* second section */
%}
S : /* empty */	{ printf("S -> epsilon\n"); }
  | '(' S ')' S { printf("S -> ( S ) S\n"); }
%ifdef ABC
    /* see how preprocessor can be used */
  | '*'         { printf("S -> *\n"); }
%endif
  ;
%%
#include <stdio.h>

int main() {
  int rv;
  printf("yyparse() = %d\n", (rv=yyparse()));
  return rv;
}

yylex() {
  int ch;

	do { ch = getchar(); } while (ch == ' ' || ch == '\n' || ch == '\t');
	if (ch == EOF) return 0;
	return ch;
}

void yyerror(const char *s, ...) {
  printf("%s\n",s);
}
