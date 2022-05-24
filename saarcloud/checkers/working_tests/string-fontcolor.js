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

// Simple case.
var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson("'_'.fontcolor('b')",'"<font color=\\"b\\">_</font>"');addReportExprJson("'<'.fontcolor('b')",'"<font color=\\"b\\"><</font>"');addReportExprJson("'_'.fontcolor(0x2A)",'"<font color=\\"42\\">_</font>"');addReportExprJson("'_'.fontcolor('\"')",'"<font color=\\"&quot;\\">_</font>"');addReportExprJson("'_'.fontcolor('\" size=\"2px')",'"<font color=\\"&quot; size=&quot;2px\\">_</font>"');addReportExprJson("String.prototype.fontcolor.call(0x2A, 0x2A)",'"<font color=\\"42\\">42</font>"');addExceptionExpr("String.prototype.fontcolor.call(undefined)",'"TypeError: Type error"');addExceptionExpr("String.prototype.fontcolor.call(null)",'"TypeError: Type error"');addReportExprJson("String.prototype.fontcolor.length","1");return RESULT