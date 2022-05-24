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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprStr(expr){RESULT.push(""+eval(expr))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}addReportExpr("L:{true;break L;false}");addExceptionExpr("if (0) { L:{ break; } }");addExceptionExpr("if (0) { L:{ continue L; } }");addExceptionExpr("if (0) { L:{ continue; } }");addExceptionExpr("if (0) { switch (1) { case 1: continue; } }");addReportExpr("A:L:{true;break L;false}");addExceptionExpr("if (0) { A:L:{ break; } }");addExceptionExpr("if (0) { A:L:{ continue L; } }");addExceptionExpr("if (0) { A:L:{ continue; } }");addReportExpr("L:A:{true;break L;false}");addExceptionExpr("if (0) { L:A:{ break; } }");addExceptionExpr("if (0) { L:A:{ continue L; } }");addExceptionExpr("if (0) { L:A:{ continue; } }");addReportExprStr("if(0){ L:for(;;) continue L; }");addReportExprStr("if(0){ L:A:for(;;) continue L; }");addReportExprStr("if(0){ A:L:for(;;) continue L; }");addExceptionExpr("if(0){ A:for(;;) L:continue L; }");addReportExprStr("if(0){ L:for(;;) A:continue L; }");addReportExprStr("if(0){ L:do continue L; while(0); }");addReportExprStr("if(0){ L:A:do continue L; while(0); }");addReportExprStr("if(0){ A:L:do continue L; while(0);}");addExceptionExpr("if(0){ A:do L:continue L; while(0); }");addReportExprStr("if(0){ L:do A:continue L; while(0); }");addReportExprStr("if(0){ L:while(0) continue L; }");addReportExprStr("if(0){ L:A:while(0) continue L; }");addReportExprStr("if(0){ A:L:while(0) continue L; }");addExceptionExpr("if(0){ A:while(0) L:continue L; }");addReportExprStr("if(0){ L:while(0) A:continue L; }");return RESULT