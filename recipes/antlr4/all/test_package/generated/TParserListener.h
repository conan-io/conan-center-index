/* parser/listener/visitor header section */

// Generated from TParser.g4 by ANTLR 4.8

#pragma once

/* listener preinclude section */

#include "antlr4-runtime.h"
#include "TParser.h"

/* listener postinclude section */

namespace antlrcpptest {

/**
 * This interface defines an abstract listener for a parse tree produced by TParser.
 */
class  TParserListener : public antlr4::tree::ParseTreeListener {
public:
/* listener public declarations/members section */

  virtual void enterMain(TParser::MainContext *ctx) = 0;
  virtual void exitMain(TParser::MainContext *ctx) = 0;

  virtual void enterDivide(TParser::DivideContext *ctx) = 0;
  virtual void exitDivide(TParser::DivideContext *ctx) = 0;

  virtual void enterAnd_(TParser::And_Context *ctx) = 0;
  virtual void exitAnd_(TParser::And_Context *ctx) = 0;

  virtual void enterConquer(TParser::ConquerContext *ctx) = 0;
  virtual void exitConquer(TParser::ConquerContext *ctx) = 0;

  virtual void enterUnused(TParser::UnusedContext *ctx) = 0;
  virtual void exitUnused(TParser::UnusedContext *ctx) = 0;

  virtual void enterUnused2(TParser::Unused2Context *ctx) = 0;
  virtual void exitUnused2(TParser::Unused2Context *ctx) = 0;

  virtual void enterStat(TParser::StatContext *ctx) = 0;
  virtual void exitStat(TParser::StatContext *ctx) = 0;

  virtual void enterExpr(TParser::ExprContext *ctx) = 0;
  virtual void exitExpr(TParser::ExprContext *ctx) = 0;

  virtual void enterReturn(TParser::ReturnContext *ctx) = 0;
  virtual void exitReturn(TParser::ReturnContext *ctx) = 0;

  virtual void enterContinue(TParser::ContinueContext *ctx) = 0;
  virtual void exitContinue(TParser::ContinueContext *ctx) = 0;

  virtual void enterId(TParser::IdContext *ctx) = 0;
  virtual void exitId(TParser::IdContext *ctx) = 0;

  virtual void enterArray(TParser::ArrayContext *ctx) = 0;
  virtual void exitArray(TParser::ArrayContext *ctx) = 0;

  virtual void enterIdarray(TParser::IdarrayContext *ctx) = 0;
  virtual void exitIdarray(TParser::IdarrayContext *ctx) = 0;

  virtual void enterAny(TParser::AnyContext *ctx) = 0;
  virtual void exitAny(TParser::AnyContext *ctx) = 0;


private:  
/* listener private declarations/members section */
};

}  // namespace antlrcpptest
