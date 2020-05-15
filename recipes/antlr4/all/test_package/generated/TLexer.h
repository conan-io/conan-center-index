/* lexer header section */

// Generated from TLexer.g4 by ANTLR 4.8

#pragma once

/* lexer precinclude section */

#include "antlr4-runtime.h"


/* lexer postinclude section */
#ifndef _WIN32
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif


namespace antlrcpptest {

/* lexer context section */

class  TLexer : public antlr4::Lexer {
public:
  enum {
    DUMMY = 1, Return = 2, Continue = 3, INT = 4, Digit = 5, ID = 6, LessThan = 7, 
    GreaterThan = 8, Equal = 9, And = 10, Colon = 11, Semicolon = 12, Plus = 13, 
    Minus = 14, Star = 15, OpenPar = 16, ClosePar = 17, OpenCurly = 18, 
    CloseCurly = 19, QuestionMark = 20, Comma = 21, String = 22, Foo = 23, 
    Bar = 24, Any = 25, Comment = 26, WS = 27, Dot = 28, DotDot = 29, Dollar = 30, 
    Ampersand = 31
  };

  enum {
    CommentsChannel = 2, DirectiveChannel = 3
  };

  enum {
    Mode1 = 1, Mode2 = 2
  };

  TLexer(antlr4::CharStream *input);
  ~TLexer();

  /* public lexer declarations section */
  bool canTestFoo() { return true; }
  bool isItFoo() { return true; }
  bool isItBar() { return true; }

  void myFooLexerAction() { /* do something*/ };
  void myBarLexerAction() { /* do something*/ };

  virtual std::string getGrammarFileName() const override;
  virtual const std::vector<std::string>& getRuleNames() const override;

  virtual const std::vector<std::string>& getChannelNames() const override;
  virtual const std::vector<std::string>& getModeNames() const override;
  virtual const std::vector<std::string>& getTokenNames() const override; // deprecated, use vocabulary instead
  virtual antlr4::dfa::Vocabulary& getVocabulary() const override;

  virtual const std::vector<uint16_t> getSerializedATN() const override;
  virtual const antlr4::atn::ATN& getATN() const override;

  virtual void action(antlr4::RuleContext *context, size_t ruleIndex, size_t actionIndex) override;
  virtual bool sempred(antlr4::RuleContext *_localctx, size_t ruleIndex, size_t predicateIndex) override;

private:
  static std::vector<antlr4::dfa::DFA> _decisionToDFA;
  static antlr4::atn::PredictionContextCache _sharedContextCache;
  static std::vector<std::string> _ruleNames;
  static std::vector<std::string> _tokenNames;
  static std::vector<std::string> _channelNames;
  static std::vector<std::string> _modeNames;

  static std::vector<std::string> _literalNames;
  static std::vector<std::string> _symbolicNames;
  static antlr4::dfa::Vocabulary _vocabulary;
  static antlr4::atn::ATN _atn;
  static std::vector<uint16_t> _serializedATN;

  /* private lexer declarations/members section */

  // Individual action functions triggered by action() above.
  void FooAction(antlr4::RuleContext *context, size_t actionIndex);
  void BarAction(antlr4::RuleContext *context, size_t actionIndex);

  // Individual semantic predicate functions triggered by sempred() above.
  bool FooSempred(antlr4::RuleContext *_localctx, size_t predicateIndex);
  bool BarSempred(antlr4::RuleContext *_localctx, size_t predicateIndex);

  struct Initializer {
    Initializer();
  };
  static Initializer _init;
};

}  // namespace antlrcpptest
