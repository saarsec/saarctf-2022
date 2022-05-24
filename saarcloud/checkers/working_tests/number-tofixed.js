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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson("(0).toFixed(0)","'0'");addReportExprJson("(0.49).toFixed(0)","'0'");addReportExprJson("(0.5).toFixed(0)","'1'");addReportExprJson("(0.51).toFixed(0)","'1'");addReportExprJson("(-0.49).toFixed(0)","'-0'");addReportExprJson("(-0.5).toFixed(0)","'-1'");addReportExprJson("(-0.51).toFixed(0)","'-1'");addReportExprJson("(0).toFixed(1)","'0.0'");addReportExprJson("(0.449).toFixed(1)","'0.4'");addReportExprJson("(0.45).toFixed(1)","'0.5'");addReportExprJson("(0.451).toFixed(1)","'0.5'");addReportExprJson("(0.5).toFixed(1)","'0.5'");addReportExprJson("(0.549).toFixed(1)","'0.5'");addReportExprJson("(0.55).toFixed(1)","'0.6'");addReportExprJson("(0.551).toFixed(1)","'0.6'");addReportExprJson("(-0.449).toFixed(1)","'-0.4'");addReportExprJson("(-0.45).toFixed(1)","'-0.5'");addReportExprJson("(-0.451).toFixed(1)","'-0.5'");addReportExprJson("(-0.5).toFixed(1)","'-0.5'");addReportExprJson("(-0.549).toFixed(1)","'-0.5'");addReportExprJson("(-0.55).toFixed(1)","'-0.6'");addReportExprJson("(-0.551).toFixed(1)","'-0.6'");var posInf=1/0;var negInf=-1/0;var nan=0/0;addReportExprJson("(0.0).toFixed(4)","0.0000");addReportExprJson("(-0.0).toFixed(4)","0.0000");addReportExprJson("(0.0).toFixed()","0");addReportExprJson("(-0.0).toFixed()","0");addReportExprJson("(1234.567).toFixed()","1235");addReportExprJson("(1234.567).toFixed(0)","1235");addReportExprJson("(1234.567).toFixed(null)","1235");addReportExprJson("(1234.567).toFixed(false)","1235");addReportExprJson("(1234.567).toFixed('foo')","1235");addReportExprJson("(1234.567).toFixed(nan)","1235");addReportExprJson("(1234.567).toFixed(1)","1234.6");addReportExprJson("(1234.567).toFixed(true)","1234.6");addReportExprJson("(1234.567).toFixed('1')","1234.6");addReportExprJson("(1234.567).toFixed(2)","1234.57");addReportExprJson("(1234.567).toFixed(2.9)","1234.57");addReportExprJson("(1234.567).toFixed(5)","1234.56700");addReportExprJson("(1234.567).toFixed(20)","1234.56700000000000727596");addExceptionExpr("(1234.567).toFixed(21)");addExceptionExpr("(1234.567).toFixed(100)");addExceptionExpr("(1234.567).toFixed(101)");addExceptionExpr("(1234.567).toFixed(-1)");addExceptionExpr("(1234.567).toFixed(-4)");addExceptionExpr("(1234.567).toFixed(-5)");addExceptionExpr("(1234.567).toFixed(-20)");addExceptionExpr("(1234.567).toFixed(-21)");addExceptionExpr("(1234.567).toFixed(posInf)");addExceptionExpr("(1234.567).toFixed(negInf)");addReportExprJson("posInf.toFixed()","Infinity");addReportExprJson("negInf.toFixed()","-Infinity");addReportExprJson("nan.toFixed()","NaN");return RESULT