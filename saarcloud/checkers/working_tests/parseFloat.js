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



var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}var nonASCIINonSpaceCharacter=String.fromCharCode(5024);var illegalUTF16Sequence=String.fromCharCode(55296);var tab=String.fromCharCode(9);var nbsp=String.fromCharCode(160);var ff=String.fromCharCode(12);var vt=String.fromCharCode(11);var cr=String.fromCharCode(13);var lf=String.fromCharCode(10);var ls=String.fromCharCode(8232);var ps=String.fromCharCode(8233);var oghamSpaceMark=String.fromCharCode(5760);var mongolianVowelSeparator=String.fromCharCode(6158);var enQuad=String.fromCharCode(8192);var emQuad=String.fromCharCode(8193);var enSpace=String.fromCharCode(8194);var emSpace=String.fromCharCode(8195);var threePerEmSpace=String.fromCharCode(8196);var fourPerEmSpace=String.fromCharCode(8197);var sixPerEmSpace=String.fromCharCode(8198);var figureSpace=String.fromCharCode(8199);var punctuationSpace=String.fromCharCode(8200);var thinSpace=String.fromCharCode(8201);var hairSpace=String.fromCharCode(8202);var narrowNoBreakSpace=String.fromCharCode(8239);var mediumMathematicalSpace=String.fromCharCode(8287);var ideographicSpace=String.fromCharCode(12288);addReportExprJson("parseFloat()","NaN");addReportExprJson("parseFloat('')","NaN");addReportExprJson("parseFloat(' ')","NaN");addReportExprJson("parseFloat(' 0')","0");addReportExprJson("parseFloat('0 ')","0");addReportExprJson("parseFloat('x0')","NaN");addReportExprJson("parseFloat('0x')","0");addReportExprJson("parseFloat(' 1')","1");addReportExprJson("parseFloat('1 ')","1");addReportExprJson("parseFloat('x1')","NaN");addReportExprJson("parseFloat('1x')","1");addReportExprJson("parseFloat(' 2.3')","2.3");addReportExprJson("parseFloat('2.3 ')","2.3");addReportExprJson("parseFloat('x2.3')","NaN");addReportExprJson("parseFloat('2.3x')","2.3");addReportExprJson("parseFloat('0x2')","0");addReportExprJson("parseFloat('1' + nonASCIINonSpaceCharacter)","1");addReportExprJson("parseFloat(nonASCIINonSpaceCharacter + '1')","NaN");addReportExprJson("parseFloat('1' + illegalUTF16Sequence)","1");addReportExprJson("parseFloat(illegalUTF16Sequence + '1')","NaN");addReportExprJson("parseFloat(tab + '1')","1");addReportExprJson("parseFloat(nbsp + '1')","1");addReportExprJson("parseFloat(ff + '1')","1");addReportExprJson("parseFloat(vt + '1')","1");addReportExprJson("parseFloat(cr + '1')","1");addReportExprJson("parseFloat(lf + '1')","1");addReportExprJson("parseFloat(ls + '1')","1");addReportExprJson("parseFloat(ps + '1')","1");addReportExprJson("parseFloat(oghamSpaceMark + '1')","1");addReportExprJson("parseFloat(mongolianVowelSeparator + '1')","NaN");addReportExprJson("parseFloat(enQuad + '1')","1");addReportExprJson("parseFloat(emQuad + '1')","1");addReportExprJson("parseFloat(enSpace + '1')","1");addReportExprJson("parseFloat(emSpace + '1')","1");addReportExprJson("parseFloat(threePerEmSpace + '1')","1");addReportExprJson("parseFloat(fourPerEmSpace + '1')","1");addReportExprJson("parseFloat(sixPerEmSpace + '1')","1");addReportExprJson("parseFloat(figureSpace + '1')","1");addReportExprJson("parseFloat(punctuationSpace + '1')","1");addReportExprJson("parseFloat(thinSpace + '1')","1");addReportExprJson("parseFloat(hairSpace + '1')","1");addReportExprJson("parseFloat(narrowNoBreakSpace + '1')","1");addReportExprJson("parseFloat(mediumMathematicalSpace + '1')","1");addReportExprJson("parseFloat(ideographicSpace + '1')","1");return RESULT