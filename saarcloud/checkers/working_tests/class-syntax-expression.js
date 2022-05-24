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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}var constructorCallCount=0;const staticMethodValue=[1];const instanceMethodValue=[2];const getterValue=[3];var setterValue=void 0;var A=class{constructor(){constructorCallCount++}static someStaticMethod(){return staticMethodValue}static get someStaticGetter(){return getterValue}static set someStaticSetter(value){setterValue=value}someInstanceMethod(){return instanceMethodValue}get someGetter(){return getterValue}set someSetter(value){setterValue=value}};addReportExprJson("constructorCallCount","0");addReportExprJson("A.someStaticMethod()","staticMethodValue");addReportExprJson("A.someStaticGetter","getterValue");addReportExprJson("setterValue = undefined; A.someStaticSetter = 123; setterValue","123");addReportExprJson("(new A).someInstanceMethod()","instanceMethodValue");addReportExprJson("constructorCallCount","1");addReportExprJson("(new A).someGetter","getterValue");addReportExprJson("constructorCallCount","2");addReportExprJson("(new A).someGetter","getterValue");addReportExprJson("setterValue = undefined; (new A).someSetter = 789; setterValue","789");addReportExprJson("(new A).__proto__","A.prototype");addReportExprJson("A.prototype.constructor","A");addExceptionExpr("x = class","'SyntaxError: Unexpected end of input'");addExceptionExpr("x = class {","'SyntaxError: Unexpected end of input'");addExceptionExpr("x = class { ( }","\"SyntaxError: Unexpected token '('\"");addExceptionExpr("x = class {}");addExceptionExpr("x = class { constructor() {} constructor() {} }","'SyntaxError: A class may only have one constructor'");addExceptionExpr("x = class { get constructor() {} }","'SyntaxError: Class constructor may not be an accessor'");addExceptionExpr("x = class { set constructor() {} }","'SyntaxError: Class constructor may not be an accessor'");addExceptionExpr("x = class { constructor() {} static constructor() { return staticMethodValue; } }");addReportExprJson("x = class { constructor() {} static constructor() { return staticMethodValue; } }; x.constructor()","staticMethodValue");addExceptionExpr("x = class { constructor() {} static prototype() {} }","\"SyntaxError: Classes may not have a static property named 'prototype'\"");addExceptionExpr("x = class { constructor() {} static get prototype() {} }","\"SyntaxError: Classes may not have a static property named 'prototype'\"");addExceptionExpr("x = class { constructor() {} static set prototype() {} }","\"SyntaxError: Classes may not have a static property named 'prototype'\"");addExceptionExpr("x = class  { constructor() {} prototype() { return instanceMethodValue; } }");addReportExprJson("x = class { constructor() {} prototype() { return instanceMethodValue; } }; (new x).prototype()","instanceMethodValue");addExceptionExpr("x = class { constructor() {} set foo(a) {} }");addExceptionExpr("x = class { constructor() {} set foo({x, y}) {} }");addExceptionExpr("x = class { constructor() {} set foo() {} }");addExceptionExpr("x = class { constructor() {} set foo(a, b) {} }");addExceptionExpr("x = class { constructor() {} get foo() {} }");addExceptionExpr("x = class { constructor() {} get foo(x) {} }");addExceptionExpr("x = class { constructor() {} get foo({x, y}) {} }");var successfullyParsed=true;return RESULT