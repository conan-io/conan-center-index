/* parser/listener/visitor header section */

// Generated from TParser.g4 by ANTLR 4.8

#pragma once

/* visitor preinclude section */

#include "antlr4-runtime.h"
#include "TParser.h"

/* visitor postinclude section */

namespace antlrcpptest {

/**
 * This class defines an abstract visitor for a parse tree
 * produced by TParser.
 */
class  TParserVisitor : public antlr4::tree::AbstractParseTreeVisitor {
public:
  /* visitor public declarations/members section */

  /**
   * Visit parse trees produced by TParser.
   */
    virtual antlrcpp::Any visitMain(TParser::MainContext *context) = 0;

    virtual antlrcpp::Any visitDivide(TParser::DivideContext *context) = 0;

    virtual antlrcpp::Any visitAnd_(TParser::And_Context *context) = 0;

    virtual antlrcpp::Any visitConquer(TParser::ConquerContext *context) = 0;

    virtual antlrcpp::Any visitUnused(TParser::UnusedContext *context) = 0;

    virtual antlrcpp::Any visitUnused2(TParser::Unused2Context *context) = 0;

    virtual antlrcpp::Any visitStat(TParser::StatContext *context) = 0;

    virtual antlrcpp::Any visitExpr(TParser::ExprContext *context) = 0;

    virtual antlrcpp::Any visitReturn(TParser::ReturnContext *context) = 0;

    virtual antlrcpp::Any visitContinue(TParser::ContinueContext *context) = 0;

    virtual antlrcpp::Any visitId(TParser::IdContext *context) = 0;

    virtual antlrcpp::Any visitArray(TParser::ArrayContext *context) = 0;

    virtual antlrcpp::Any visitIdarray(TParser::IdarrayContext *context) = 0;

    virtual antlrcpp::Any visitAny(TParser::AnyContext *context) = 0;


private:  
/* visitor private declarations/members section */
};

}  // namespace antlrcpptest
