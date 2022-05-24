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



var RESULT=[];function addReportExprStr(expr){RESULT.push(""+eval(expr))}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function leftConstantRightSimple(a){return.1*(a*a)}addReportExprJson("leftConstantRightSimple(2)","0.4");function leftConstantRightComplex(a){return.1*(a*a+a)}addReportExprJson("leftConstantRightComplex(1)","0.2");function leftSimpleRightConstant(a){return a*a*.1}addReportExprJson("leftSimpleRightConstant(2)","0.4");function leftComplexRightConstant(a){return.1*(a*a+a)}addReportExprJson("leftComplexRightConstant(1)","0.2");function leftThisRightSimple(a){return this*(a*a)}addReportExprStr("leftThisRightSimple(2)");addReportExprJson("leftThisRightSimple.call(2, 2)","8");function leftThisRightComplex(a){return this*(a*a+a)}addReportExprStr("leftThisRightComplex(2)");addReportExprJson("leftThisRightComplex.call(2, 2)","12");function leftSimpleRightThis(a){return a*a*this}addReportExprStr("leftSimpleRightThis(2)");addReportExprJson("leftSimpleRightThis.call(2, 2)","8");function leftComplexRightThis(a){return(a*a+a)*this}addReportExprStr("leftComplexRightThis(2)");addReportExprJson("leftComplexRightThis.call(2, 2)","12");return RESULT