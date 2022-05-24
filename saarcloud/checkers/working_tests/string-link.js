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



// This test is based on http://mathias.html5.org/tests/javascript/string/.

// Check that the quotation mark is correctly escaped.
var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson("'_'.link('\"')",'"<a href=\\"&quot;\\">_</a>"');addReportExprJson("'_'.link('b')",'"<a href=\\"b\\">_</a>"');addReportExprJson("'<'.link('b')",'"<a href=\\"b\\"><</a>"');addReportExprJson("'_'.link(0x2A)",'"<a href=\\"42\\">_</a>"');addReportExprJson("'_'.link('\"')",'"<a href=\\"&quot;\\">_</a>"');addReportExprJson("'_'.link('\" target=\"_blank')",'"<a href=\\"&quot; target=&quot;_blank\\">_</a>"');addReportExprJson("String.prototype.link.call(0x2A, 0x2A)",'"<a href=\\"42\\">42</a>"');addExceptionExpr("String.prototype.link.call(undefined)",'"TypeError: Type error"');addExceptionExpr("String.prototype.link.call(null)",'"TypeError: Type error"');addReportExprJson("String.prototype.link.length","1");return RESULT