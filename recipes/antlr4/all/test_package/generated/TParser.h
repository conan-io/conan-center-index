/* parser/listener/visitor header section */

// Generated from TParser.g4 by ANTLR 4.8

#pragma once

/* parser precinclude section */

#include "antlr4-runtime.h"


/* parser postinclude section */
#ifndef _WIN32
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif


namespace antlrcpptest {

/* parser context section */

class  TParser : public antlr4::Parser {
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
    RuleMain = 0, RuleDivide = 1, RuleAnd_ = 2, RuleConquer = 3, RuleUnused = 4, 
    RuleUnused2 = 5, RuleStat = 6, RuleExpr = 7, RuleFlowControl = 8, RuleId = 9, 
    RuleArray = 10, RuleIdarray = 11, RuleAny = 12
  };

  TParser(antlr4::TokenStream *input);
  ~TParser();

  virtual std::string getGrammarFileName() const override;
  virtual const antlr4::atn::ATN& getATN() const override { return _atn; };
  virtual const std::vector<std::string>& getTokenNames() const override { return _tokenNames; }; // deprecated: use vocabulary instead.
  virtual const std::vector<std::string>& getRuleNames() const override;
  virtual antlr4::dfa::Vocabulary& getVocabulary() const override;


  /* public parser declarations/members section */
  bool myAction() { return true; }
  bool doesItBlend() { return true; }
  void cleanUp() {}
  void doInit() {}
  void doAfter() {}


  class MainContext;
  class DivideContext;
  class And_Context;
  class ConquerContext;
  class UnusedContext;
  class Unused2Context;
  class StatContext;
  class ExprContext;
  class FlowControlContext;
  class IdContext;
  class ArrayContext;
  class IdarrayContext;
  class AnyContext; 

  class  MainContext : public antlr4::ParserRuleContext {
  public:
    MainContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *EOF();
    std::vector<StatContext *> stat();
    StatContext* stat(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  MainContext* main();

  class  DivideContext : public antlr4::ParserRuleContext {
  public:
    DivideContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();
    And_Context *and_();
    antlr4::tree::TerminalNode *GreaterThan();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  DivideContext* divide();

  class  And_Context : public antlr4::ParserRuleContext {
  public:
    And_Context(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *And();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  And_Context* and_();

  class  ConquerContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *idToken = nullptr;;
    ConquerContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<DivideContext *> divide();
    DivideContext* divide(size_t i);
    And_Context *and_();
    antlr4::tree::TerminalNode *ID();
    std::vector<antlr4::tree::TerminalNode *> LessThan();
    antlr4::tree::TerminalNode* LessThan(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  ConquerContext* conquer();

  class  UnusedContext : public antlr4::ParserRuleContext {
  public:
    double input = 111;
    double calculated;
    int _a;
    double _b;
    int _c;
    UnusedContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    UnusedContext(antlr4::ParserRuleContext *parent, size_t invokingState, double input = 111);
    virtual size_t getRuleIndex() const override;
    StatContext *stat();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  UnusedContext* unused(double input = 111);

  class  Unused2Context : public antlr4::ParserRuleContext {
  public:
    Unused2Context(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<antlr4::tree::TerminalNode *> Semicolon();
    antlr4::tree::TerminalNode* Semicolon(size_t i);
    std::vector<UnusedContext *> unused();
    UnusedContext* unused(size_t i);
    antlr4::tree::TerminalNode *Colon();
    antlr4::tree::TerminalNode *Plus();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  Unused2Context* unused2();

  class  StatContext : public antlr4::ParserRuleContext {
  public:
    StatContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    std::vector<ExprContext *> expr();
    ExprContext* expr(size_t i);
    antlr4::tree::TerminalNode *Equal();
    antlr4::tree::TerminalNode *Semicolon();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  StatContext* stat();

  class  ExprContext : public antlr4::ParserRuleContext {
  public:
    TParser::IdContext *identifier = nullptr;;
    ExprContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *OpenPar();
    std::vector<ExprContext *> expr();
    ExprContext* expr(size_t i);
    antlr4::tree::TerminalNode *ClosePar();
    IdContext *id();
    FlowControlContext *flowControl();
    antlr4::tree::TerminalNode *INT();
    antlr4::tree::TerminalNode *String();
    antlr4::tree::TerminalNode *Star();
    antlr4::tree::TerminalNode *Plus();
    antlr4::tree::TerminalNode *QuestionMark();
    antlr4::tree::TerminalNode *Colon();
    antlr4::tree::TerminalNode *Equal();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  ExprContext* expr();
  ExprContext* expr(int precedence);
  class  FlowControlContext : public antlr4::ParserRuleContext {
  public:
    FlowControlContext(antlr4::ParserRuleContext *parent, size_t invokingState);
   
    FlowControlContext() = default;
    void copyFrom(FlowControlContext *context);
    using antlr4::ParserRuleContext::copyFrom;

    virtual size_t getRuleIndex() const override;

   
  };

  class  ReturnContext : public FlowControlContext {
  public:
    ReturnContext(FlowControlContext *ctx);

    antlr4::tree::TerminalNode *Return();
    ExprContext *expr();
    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
  };

  class  ContinueContext : public FlowControlContext {
  public:
    ContinueContext(FlowControlContext *ctx);

    antlr4::tree::TerminalNode *Continue();
    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
  };

  FlowControlContext* flowControl();

  class  IdContext : public antlr4::ParserRuleContext {
  public:
    IdContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *ID();

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  IdContext* id();

  class  ArrayContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *intToken = nullptr;;
    std::vector<antlr4::Token *> el;;
    ArrayContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *OpenCurly();
    antlr4::tree::TerminalNode *CloseCurly();
    std::vector<antlr4::tree::TerminalNode *> INT();
    antlr4::tree::TerminalNode* INT(size_t i);
    std::vector<antlr4::tree::TerminalNode *> Comma();
    antlr4::tree::TerminalNode* Comma(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  ArrayContext* array();

  class  IdarrayContext : public antlr4::ParserRuleContext {
  public:
    TParser::IdContext *idContext = nullptr;;
    std::vector<IdContext *> element;;
    IdarrayContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;
    antlr4::tree::TerminalNode *OpenCurly();
    antlr4::tree::TerminalNode *CloseCurly();
    std::vector<IdContext *> id();
    IdContext* id(size_t i);
    std::vector<antlr4::tree::TerminalNode *> Comma();
    antlr4::tree::TerminalNode* Comma(size_t i);

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  IdarrayContext* idarray();

  class  AnyContext : public antlr4::ParserRuleContext {
  public:
    antlr4::Token *t = nullptr;;
    AnyContext(antlr4::ParserRuleContext *parent, size_t invokingState);
    virtual size_t getRuleIndex() const override;

    virtual void enterRule(antlr4::tree::ParseTreeListener *listener) override;
    virtual void exitRule(antlr4::tree::ParseTreeListener *listener) override;

    virtual antlrcpp::Any accept(antlr4::tree::ParseTreeVisitor *visitor) override;
   
  };

  AnyContext* any();


  virtual bool sempred(antlr4::RuleContext *_localctx, size_t ruleIndex, size_t predicateIndex) override;
  bool divideSempred(DivideContext *_localctx, size_t predicateIndex);
  bool conquerSempred(ConquerContext *_localctx, size_t predicateIndex);
  bool exprSempred(ExprContext *_localctx, size_t predicateIndex);

private:
  static std::vector<antlr4::dfa::DFA> _decisionToDFA;
  static antlr4::atn::PredictionContextCache _sharedContextCache;
  static std::vector<std::string> _ruleNames;
  static std::vector<std::string> _tokenNames;

  static std::vector<std::string> _literalNames;
  static std::vector<std::string> _symbolicNames;
  static antlr4::dfa::Vocabulary _vocabulary;
  static antlr4::atn::ATN _atn;
  static std::vector<uint16_t> _serializedATN;

  /* private parser declarations section */

  struct Initializer {
    Initializer();
  };
  static Initializer _init;
};

}  // namespace antlrcpptest
