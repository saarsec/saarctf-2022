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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}var baseMethodValue={};var valueInSetter=null;class Base{constructor(){}baseMethod(){return baseMethodValue}chainMethod(){return"base"}static staticMethod(){return"base3"}}class Derived extends Base{constructor(){super()}chainMethod(){return[super.chainMethod(),"derived"]}callBaseMethod(){return super.baseMethod()}get callBaseMethodInGetter(){return super["baseMethod"]()}set callBaseMethodInSetter(x){valueInSetter=super.baseMethod()}get baseMethodInGetterSetter(){return super.baseMethod}set baseMethodInGetterSetter(x){valueInSetter=super["baseMethod"]}static staticMethod(){return super.staticMethod()}}class SecondDerived extends Derived{constructor(){super()}chainMethod(){return super.chainMethod().concat(["secondDerived"])}}addReportExpr("(new Base) instanceof Base");addReportExpr("(new Derived) instanceof Derived");addReportExprJson("(new Derived).callBaseMethod()","baseMethodValue");addReportExprJson("x = (new Derived).callBaseMethod; x()","baseMethodValue");addReportExprJson("(new Derived).callBaseMethodInGetter","baseMethodValue");addReportExprJson("(new Derived).callBaseMethodInSetter = 1; valueInSetter","baseMethodValue");addReportExprJson("(new Derived).baseMethodInGetterSetter","(new Base).baseMethod");addReportExprJson("(new Derived).baseMethodInGetterSetter = 1; valueInSetter","(new Base).baseMethod");addReportExprJson("Derived.staticMethod()",'"base3"');addReportExprJson("(new SecondDerived).chainMethod()",'["base", "derived", "secondDerived"]');addExceptionExpr("x = class extends Base { constructor() { super(); } super() {} }");addExceptionExpr("x = class extends Base { constructor() { super(); } method() { super() } }","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("x = class extends Base { constructor() { super(); } method() { super } }","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("x = class extends Base { constructor() { super(); } method() { return new super } }","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr('x = class extends Base { constructor() { super(); } method1() { delete (super.foo) } method2() { delete super["foo"] } }');addExceptionExpr("(new x).method1()","\"ReferenceError: Unsupported reference to 'super'\"");addExceptionExpr("(new x).method2()","\"ReferenceError: Unsupported reference to 'super'\"");addReportExpr("new (class { constructor() { return undefined; } }) instanceof Object");addReportExpr("new (class { constructor() { return 1; } }) instanceof Object");addExceptionExpr("new (class extends Base { constructor() { return undefined } })");addReportExpr("new (class extends Base { constructor() { super(); return undefined } }) instanceof Object");addReportExprJson("x = { }; new (class extends Base { constructor() { return x } });","x");addReportExpr("x instanceof Base");addExceptionExpr("new (class extends Base { constructor() { } })","\"ReferenceError: Must call super constructor in derived class before accessing 'this' or returning from derived constructor\"");addExceptionExpr("new (class extends Base { constructor() { return 1; } })",'"TypeError: Derived constructors may only return object or undefined"');addExceptionExpr("new (class extends null { constructor() { return undefined } })");addExceptionExpr("new (class extends null { constructor() { super(); return undefined } })",'"TypeError: Super constructor null of anonymous class is not a constructor"');addReportExprJson("x = { }; new (class extends null { constructor() { return x } });","x");addReportExpr("x instanceof Object");addExceptionExpr("new (class extends null { constructor() { } })","\"ReferenceError: Must call super constructor in derived class before accessing 'this' or returning from derived constructor\"");addExceptionExpr("new (class extends null { constructor() { return 1; } })",'"TypeError: Derived constructors may only return object or undefined"');addExceptionExpr("new (class extends null { constructor() { super() } })",'"TypeError: Super constructor null of anonymous class is not a constructor"');addExceptionExpr("new (class { constructor() { super() } })","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("function x() { super(); }","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("new (class extends Object { constructor() { function x() { super() } } })","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("new (class extends Object { constructor() { function x() { super.method } } })","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("function x() { super.method(); }","\"SyntaxError: 'super' keyword unexpected here\"");addExceptionExpr("function x() { super(); }","\"SyntaxError: 'super' keyword unexpected here\"");var successfullyParsed=true;return RESULT