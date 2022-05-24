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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}addExceptionExpr("class A { foo() ; { } }","\"SyntaxError: Unexpected token ';'\"");addExceptionExpr("class A { get foo;() { } }","\"SyntaxError: Unexpected token ';'\"");addExceptionExpr("class A { get foo() ; { } }","\"SyntaxError: Unexpected token ';'\"");addExceptionExpr("class A { set foo;(x) { } }","\"SyntaxError: Unexpected token ';'\"");addExceptionExpr("class A { set foo(x) ; { } }","\"SyntaxError: Unexpected token ';'\"");addExceptionExpr("class A { ; }");addExceptionExpr("class A { foo() { } ; }");addExceptionExpr("class A { get foo() { } ; }");addExceptionExpr("class A { set foo(x) { } ; }");addExceptionExpr("class A { static foo() { } ; }");addExceptionExpr("class A { static get foo() { } ; }");addExceptionExpr("class A { static set foo(x) { } ; }");addExceptionExpr("class A { ; foo() { } }");addExceptionExpr("class A { ; get foo() { } }");addExceptionExpr("class A { ; set foo(x) { } }");addExceptionExpr("class A { ; static foo() { } }");addExceptionExpr("class A { ; static get foo() { } }");addExceptionExpr("class A { ; static set foo(x) { } }");addExceptionExpr("class A { foo() { } ; foo() {} }");addExceptionExpr("class A { foo() { } ; get foo() {} }");addExceptionExpr("class A { foo() { } ; set foo(x) {} }");addExceptionExpr("class A { foo() { } ; static foo() {} }");addExceptionExpr("class A { foo() { } ; static get foo() {} }");addExceptionExpr("class A { foo() { } ; static set foo(x) {} }");addExceptionExpr("class A { get foo() { } ; foo() {} }");addExceptionExpr("class A { get foo() { } ; get foo() {} }");addExceptionExpr("class A { get foo() { } ; set foo(x) {} }");addExceptionExpr("class A { get foo() { } ; static foo() {} }");addExceptionExpr("class A { get foo() { } ; static get foo() {} }");addExceptionExpr("class A { get foo() { } ; static set foo(x) {} }");addExceptionExpr("class A { set foo(x) { } ; foo() {} }");addExceptionExpr("class A { set foo(x) { } ; get foo() {} }");addExceptionExpr("class A { set foo(x) { } ; set foo(x) {} }");addExceptionExpr("class A { set foo(x) { } ; static foo() {} }");addExceptionExpr("class A { set foo(x) { } ; static get foo() {} }");addExceptionExpr("class A { set foo(x) { } ; static set foo(x) {} }");addExceptionExpr("class A { static foo() { } ; foo() {} }");addExceptionExpr("class A { static foo() { } ; get foo() {} }");addExceptionExpr("class A { static foo() { } ; set foo(x) {} }");addExceptionExpr("class A { static foo() { } ; static foo() {} }");addExceptionExpr("class A { static foo() { } ; static get foo() {} }");addExceptionExpr("class A { static foo() { } ; static set foo(x) {} }");addExceptionExpr("class A { static get foo() { } ; foo() {} }");addExceptionExpr("class A { static get foo() { } ; get foo() {} }");addExceptionExpr("class A { static get foo() { } ; set foo(x) {} }");addExceptionExpr("class A { static get foo() { } ; static foo() {} }");addExceptionExpr("class A { static get foo() { } ; static get foo() {} }");addExceptionExpr("class A { static get foo() { } ; static set foo(x) {} }");addExceptionExpr("class A { static set foo(x) { } ; foo() {} }");addExceptionExpr("class A { static set foo(x) { } ; get foo() {} }");addExceptionExpr("class A { static set foo(x) { } ; set foo(x) {} }");addExceptionExpr("class A { static set foo(x) { } ; static foo() {} }");addExceptionExpr("class A { static set foo(x) { } ; static get foo() {} }");addExceptionExpr("class A { static set foo(x) { } ; static set foo(x) {} }");var successfullyParsed=true;return RESULT