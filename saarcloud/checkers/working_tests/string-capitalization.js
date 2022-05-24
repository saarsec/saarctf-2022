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

var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}addReportExprJson('String("A𐐀").toLowerCase()','"a𐐨"');addReportExprJson('String("a𐐨").toUpperCase()','"A𐐀"');addReportExprJson('String("ΚΟΣΜΟΣ ΚΟΣΜΟΣ").toLowerCase()','"κοσμος κοσμος"');addReportExprJson('String("ß").toUpperCase()','"SS"');addReportExprJson('String("ŉ").toUpperCase()','"ʼN"');addReportExprJson('String("ǰ").toUpperCase()','"J̌"');addReportExprJson('String("ﬃ").toUpperCase()','"FFI"');addReportExprJson('String("FFI").toLowerCase()','"ffi"');addReportExprJson('String("Ĳ").toLowerCase()','"ĳ"');function createExpected(){expected={};for(var i=0;i<arguments.length;i++){var s=String.fromCharCode(arguments[i]);expected[s]=true}return expected}var expected=createExpected(42893,613);addReportExpr("expected[String.fromCharCode(0xA78D).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0x0265).toUpperCase()]");var expected=createExpected(4295,11559);addReportExpr("expected[String.fromCharCode(0x10C7).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0x2D27).toUpperCase()]");var expected=createExpected(4301,11565);addReportExpr("expected[String.fromCharCode(0x2D2D).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0x10CD).toUpperCase()]");var expected=createExpected(11506,11507);addReportExpr("expected[String.fromCharCode(0x2CF2).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0x2CF3).toUpperCase()]");var expected=createExpected(42898,42899);addReportExpr("expected[String.fromCharCode(0xA792).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0xA793).toUpperCase()]");var expected=createExpected(42922,614);addReportExpr("expected[String.fromCharCode(0xA7AA).toLowerCase()]");addReportExpr("expected[String.fromCharCode(0x0266).toUpperCase()]");return RESULT