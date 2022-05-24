// Copyright 2015 the V8 project authors. All rights reserved.
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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}class A{}class B extends A{}addReportExpr("new A instanceof A");addExceptionExpr("A()","\"TypeError: Class constructor A cannot be invoked without 'new'\"");addReportExpr("A.prototype.constructor instanceof Function");addReportExprJson("A.prototype.constructor.name",'"A"');addReportExpr("new B instanceof A; new B instanceof A");addExceptionExpr("B()","\"TypeError: Class constructor B cannot be invoked without 'new'\"");addReportExprJson("B.prototype.constructor.name",'"B"');addReportExpr("A !== B");addReportExpr("A.prototype.constructor !== B.prototype.constructor");addReportExprJson("new (class extends (class { constructor(a, b) { return [a, b]; } }) {})(1, 2)","[1, 2]");var successfullyParsed=true;return RESULT