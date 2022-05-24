// Copyright 2013 the V8 project authors. All rights reserved.
// Copyright (C) 2005, 2006, 2007, 2008, 2009 Apple Inc. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1.  Redistributions of source code must retain the above copyright
//     notice, this list of conditions and the following disclaimer.
// 2.  Redistributions in binary form must reproduce the above copyright
//     notice, this list of conditions and the following disclaimer in the
//     documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY APPLE INC. AND ITS CONTRIBUTORS ``AS IS'' AND ANY
// EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL APPLE INC. OR ITS CONTRIBUTORS BE LIABLE FOR ANY
// DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
// ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson("(0.999).toPrecision(1)","1");addReportExprJson("(0.999).toPrecision(2)","1.0");addReportExprJson("(0.999).toPrecision(3)","0.999");var posInf=1/0;var negInf=-1/0;var nan=0/0;addReportExprJson("(0.0).toPrecision(4)","0.000");addReportExprJson("(-0.0).toPrecision(4)","0.000");addReportExprJson("(0.0).toPrecision()","0");addReportExprJson("(-0.0).toPrecision()","0");addReportExprJson("(1234.567).toPrecision()","1234.567");addExceptionExpr("(1234.567).toPrecision(0)");addExceptionExpr("(1234.567).toPrecision(null)");addExceptionExpr("(1234.567).toPrecision(false)");addExceptionExpr("(1234.567).toPrecision('foo')");addExceptionExpr("(1234.567).toPrecision(-1)");addReportExprJson("(1234.567).toPrecision(1)","1e+3");addReportExprJson("(1234.567).toPrecision(true)","1e+3");addReportExprJson("(1234.567).toPrecision('1')","1e+3");addReportExprJson("(1234.567).toPrecision(2)","1.2e+3");addReportExprJson("(1234.567).toPrecision(2.9)","1.2e+3");addReportExprJson("(1234.567).toPrecision(5)","1234.6");addReportExprJson("(1234.567).toPrecision(21)","1234.56700000000000728");addExceptionExpr("(1234.567).toPrecision(22)");addExceptionExpr("(1234.567).toPrecision(100)");addExceptionExpr("(1234.567).toPrecision(101)");addExceptionExpr("(1234.567).toPrecision(posInf)");addExceptionExpr("(1234.567).toPrecision(negInf)");addExceptionExpr("(1234.567).toPrecision(nan)");addReportExprJson("posInf.toPrecision()","Infinity");addReportExprJson("negInf.toPrecision()","-Infinity");addReportExprJson("nan.toPrecision()","NaN");return RESULT