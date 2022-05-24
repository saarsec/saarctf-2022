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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson('/\\x{41}/.exec("yA1")',"null");addReportExprJson('/[\\x{41}]/.exec("yA1").toString()','"1"');addReportExprJson('/\\x1g/.exec("x1g").toString()','"x1g"');addReportExprJson('/[\\x1g]/.exec("x").toString()','"x"');addReportExprJson('/[\\x1g]/.exec("1").toString()','"1"');addReportExprJson('/\\2147483648/.exec(String.fromCharCode(140) + "7483648").toString()','String.fromCharCode(140) + "7483648"');addReportExprJson('/\\4294967296/.exec("\\"94967296").toString()','"\\"94967296"');addReportExprJson('/\\8589934592/.exec("\\\\8589934592").toString()','"\\\\8589934592"');addReportExprJson('"\\nAbc\\n".replace(/(\\n)[^\\n]+$/, "$1")','"\\nAbc\\n"');addReportExprJson('/x$/.exec("x\\n")',"null");addExceptionExpr("/x++/");addReportExprJson('/[]]/.exec("]")',"null");addReportExprJson('/\\060/.exec("y01").toString()','"0"');addReportExprJson('/[\\060]/.exec("y01").toString()','"0"');addReportExprJson('/\\606/.exec("y06").toString()','"06"');addReportExprJson('/[\\606]/.exec("y06").toString()','"0"');addReportExprJson('/[\\606]/.exec("y6").toString()','"6"');addReportExprJson('/\\101/.exec("yA1").toString()','"A"');addReportExprJson('/[\\101]/.exec("yA1").toString()','"A"');addReportExprJson('/\\1011/.exec("yA1").toString()','"A1"');addReportExprJson('/[\\1011]/.exec("yA1").toString()','"A"');addReportExprJson('/[\\1011]/.exec("y1").toString()','"1"');addReportExprJson('/\\10q/.exec("y" + String.fromCharCode(8) + "q").toString()','String.fromCharCode(8) + "q"');addReportExprJson('/[\\10q]/.exec("y" + String.fromCharCode(8) + "q").toString()',"String.fromCharCode(8)");addReportExprJson('/\\1q/.exec("y" + String.fromCharCode(1) + "q").toString()','String.fromCharCode(1) + "q"');addReportExprJson('/[\\1q]/.exec("y" + String.fromCharCode(1) + "q").toString()',"String.fromCharCode(1)");addReportExprJson('/[\\1q]/.exec("yq").toString()','"q"');addReportExprJson('/\\8q/.exec("\\\\8q").toString()','"\\\\8q"');addReportExprJson('/[\\8q]/.exec("y8q").toString()','"8"');addReportExprJson('/[\\8q]/.exec("yq").toString()','"q"');addReportExprJson('/(x)\\1q/.exec("xxq").toString()','"xxq,x"');addReportExprJson('/(x)[\\1q]/.exec("xxq").toString()','"xq,x"');addReportExprJson('/(x)[\\1q]/.exec("xx" + String.fromCharCode(1)).toString()','"x" + String.fromCharCode(1) + ",x"');return RESULT