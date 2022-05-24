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



// References to trim(), trimLeft() and trimRight() functions for testing Function's *.call() and *.apply() methods
var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}const trim=String.prototype.trim;const trimStart=String.prototype.trimStart;const trimLeft=String.prototype.trimLeft;const trimEnd=String.prototype.trimEnd;const trimRight=String.prototype.trimRight;const whitespace=[{s:"\t",t:"HORIZONTAL TAB"},{s:"\n",t:"LINE FEED OR NEW LINE"},{s:"\v",t:"VERTICAL TAB"},{s:"\f",t:"FORMFEED"},{s:"\r",t:"CARRIAGE RETURN"},{s:" ",t:"SPACE"},{s:" ",t:"NO-BREAK SPACE"},{s:" ",t:"EN QUAD"},{s:" ",t:"EM QUAD"},{s:" ",t:"EN SPACE"},{s:" ",t:"EM SPACE"},{s:" ",t:"THREE-PER-EM SPACE"},{s:" ",t:"FOUR-PER-EM SPACE"},{s:" ",t:"SIX-PER-EM SPACE"},{s:" ",t:"FIGURE SPACE"},{s:" ",t:"PUNCTUATION SPACE"},{s:" ",t:"THIN SPACE"},{s:" ",t:"HAIR SPACE"},{s:"　",t:"IDEOGRAPHIC SPACE"},{s:"\u2028",t:"LINE SEPARATOR"},{s:"\u2029",t:"PARAGRAPH SEPARATOR"},{s:"​",t:"ZERO WIDTH SPACE (category Cf)"}];let wsString="";for(let i=0;i<whitespace.length;i++){addReportExprJson("whitespace["+i+"].s.trim()","''");addReportExprJson("whitespace["+i+"].s.trimStart()","''");addReportExprJson("whitespace["+i+"].s.trimLeft()","''");addReportExprJson("whitespace["+i+"].s.trimEnd()","''");addReportExprJson("whitespace["+i+"].s.trimRight()","''");wsString+=whitespace[i].s}const testString="foo bar";const trimString=wsString+testString+wsString;const leftTrimString=testString+wsString;const rightTrimString=wsString+testString;addReportExprJson("wsString.trim()","''");addReportExprJson("wsString.trimStart()","''");addReportExprJson("wsString.trimLeft()","''");addReportExprJson("wsString.trimEnd()","''");addReportExprJson("wsString.trimRight()","''");addReportExprJson("trimString.trim()","testString");addReportExprJson("trimString.trimStart()","leftTrimString");addReportExprJson("trimString.trimLeft()","leftTrimString");addReportExprJson("trimString.trimEnd()","rightTrimString");addReportExprJson("trimString.trimRight()","rightTrimString");addReportExprJson("leftTrimString.trim()","testString");addReportExprJson("leftTrimString.trimStart()","leftTrimString");addReportExprJson("leftTrimString.trimLeft()","leftTrimString");addReportExprJson("leftTrimString.trimEnd()","testString");addReportExprJson("leftTrimString.trimRight()","testString");addReportExprJson("rightTrimString.trim()","testString");addReportExprJson("rightTrimString.trimStart()","testString");addReportExprJson("rightTrimString.trimLeft()","testString");addReportExprJson("rightTrimString.trimEnd()","rightTrimString");addReportExprJson("rightTrimString.trimRight()","rightTrimString");const testValues=["0","Infinity","NaN","true","false","({})","({toString:function(){return 'wibble'}})","['an','array']"];for(const testValue of testValues){addReportExprJson("trim.call("+testValue+")","'"+eval(testValue)+"'");addReportExprJson("trimStart.call("+testValue+")","'"+eval(testValue)+"'");addReportExprJson("trimLeft.call("+testValue+")","'"+eval(testValue)+"'");addReportExprJson("trimEnd.call("+testValue+")","'"+eval(testValue)+"'");addReportExprJson("trimRight.call("+testValue+")","'"+eval(testValue)+"'")}return RESULT