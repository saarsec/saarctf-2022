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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprStr(expr){RESULT.push(""+eval(expr))}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}function obj(){return Object.defineProperty({a:1,b:2},"g",{get:function(){return"getter"}})}function test(obj){obj.c=3;obj.b=4;delete obj.a;var result="";for(key in obj)result+="("+key+":"+obj[key]+")";if(Object.isSealed(obj))result+="S";if(Object.isFrozen(obj))result+="F";if(Object.isExtensible(obj))result+="E";return result}function seal(obj){Object.seal(obj);return obj}function freeze(obj){Object.freeze(obj);return obj}function preventExtensions(obj){Object.preventExtensions(obj);return obj}function inextensible(){}function sealed(){}function frozen(){}preventExtensions(inextensible);seal(sealed);freeze(frozen);new inextensible;new sealed;new frozen;inextensible.prototype.prototypeExists=true;sealed.prototype.prototypeExists=true;frozen.prototype.prototypeExists=true;addReportExpr("(new inextensible).prototypeExists");addReportExpr("(new sealed).prototypeExists");addReportExpr("(new frozen).prototypeExists");addReportExprJson("test(obj())",'"(b:4)(c:3)E"');addReportExprJson("test(preventExtensions(obj()))",'"(b:4)"');addReportExprJson("test(seal(obj()))",'"(a:1)(b:4)S"');addReportExprJson("test(freeze(obj()))",'"(a:1)(b:2)SF"');addReportExprJson("Object.preventExtensions(Math.sin)","Math.sin");addExceptionExpr('var o = {}; Object.preventExtensions(o); o.__proto__ = { newProp: "Should not see this" }; o.newProp;');addExceptionExpr('"use strict"; var o = {}; Object.preventExtensions(o); o.__proto__ = { newProp: "Should not see this" }; o.newProp;');addReportExprJson("Object.preventExtensions(Math); Math.sqrt(4)","2");addReportExprStr("var arr = Object.preventExtensions([]); arr[0] = 42; arr[0]");addReportExprJson("var arr = Object.preventExtensions([]); arr[0] = 42; arr.length","0");addExceptionExpr('"use strict"; var arr = Object.preventExtensions([]); arr[0] = 42; arr[0]');function Constructor(){}Constructor.prototype.foo=1;Object.freeze(Constructor.prototype);var obj=new Constructor;obj.foo=2;addReportExprJson("obj.foo","1");var func=freeze((function foo(){}));addReportExpr("Object.isFrozen(func)");func.prototype=42;addReportExpr("func.prototype === 42");addReportExpr('Object.getOwnPropertyDescriptor(func, "prototype").writable');var strictFunc=freeze((function foo(){"use strict"}));addReportExpr("Object.isFrozen(strictFunc)");strictFunc.prototype=42;addReportExpr("strictFunc.prototype === 42");addReportExpr('Object.getOwnPropertyDescriptor(strictFunc, "prototype").writable');var array=freeze([0,1,2]);addReportExpr("Object.isFrozen(array)");array[0]=3;addReportExprJson("array[0]","0");addReportExpr('Object.getOwnPropertyDescriptor(array, "length").writable');var args=freeze(function(){return arguments}(0,1,2));addReportExpr("Object.isFrozen(args)");args[0]=3;addReportExprJson("args[0]","0");addReportExpr('Object.getOwnPropertyDescriptor(args, "length").writable');addReportExpr('Object.getOwnPropertyDescriptor(args, "callee").writable');function preventExtensionsFreezeIsFrozen(x){Object.preventExtensions(x);Object.freeze(x);return Object.isFrozen(x)}addReportExpr("preventExtensionsFreezeIsFrozen(function foo(){})");addReportExpr('preventExtensionsFreezeIsFrozen(function foo(){ "use strict"; })');addReportExpr("preventExtensionsFreezeIsFrozen([0,1,2])");addReportExpr("preventExtensionsFreezeIsFrozen((function(){ return arguments; })(0,1,2))");addReportExpr("Object.getOwnPropertyDescriptor(freeze({0:0}), 0).configurable");addReportExpr("Object.getOwnPropertyDescriptor(freeze({10000001:0}), 10000001).configurable");return RESULT