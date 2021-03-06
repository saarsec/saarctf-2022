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



// Basic test for ranges - one to three and five are in regexp, four is not, and '-' should not match
var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}var regexp01=/[1-35]+/.exec("-12354");addReportExprJson("regexp01.toString()",'"1235"');var regexp01a=/[\s1-35]+/.exec("-123 54");addReportExprJson("regexp01a.toString()",'"123 5"');var regexp01b=/[1\s-35]+/.exec("21-3 54");addReportExprJson("regexp01b.toString()",'"1-3 5"');var regexp01c=/[1-\s35]+/.exec("21-3 54");addReportExprJson("regexp01c.toString()",'"1-3 5"');var regexp01d=/[1-3\s5]+/.exec("-123 54");addReportExprJson("regexp01d.toString()",'"123 5"');var regexp01e=/[1-35\s5]+/.exec("-123 54");addReportExprJson("regexp01e.toString()",'"123 5"');var regexp01f=/[-3]+/.exec("2-34");addReportExprJson("regexp01f.toString()",'"-3"');var regexp01g=/[2-]+/.exec("12-3");addReportExprJson("regexp01g.toString()",'"2-"');var regexp02=/[1\-35]+/.exec("21-354");addReportExprJson("regexp02.toString()",'"1-35"');var regexp02a=/[\s1\-35]+/.exec("21-3 54");addReportExprJson("regexp02a.toString()",'"1-3 5"');var regexp02b=/[1\s\-35]+/.exec("21-3 54");addReportExprJson("regexp02b.toString()",'"1-3 5"');var regexp02c=/[1\-\s35]+/.exec("21-3 54");addReportExprJson("regexp02c.toString()",'"1-3 5"');var regexp02d=/[1\-3\s5]+/.exec("21-3 54");addReportExprJson("regexp02d.toString()",'"1-3 5"');var regexp02e=/[1\-35\s5]+/.exec("21-3 54");addReportExprJson("regexp02e.toString()",'"1-3 5"');var regexp03a=/[\--0]+/.exec(",-.01");addReportExprJson("regexp03a.toString()",'"-.0"');var regexp03b=/[+-\-]+/.exec("*+,-.");addReportExprJson("regexp03b.toString()",'"+,-"');var bug21232=/^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]*$/.test("@");addReportExprJson("bug21232","false");return RESULT