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



var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function forIn1(){var result=[];var o={x:1};for(var p in o)result.push(p);return result}forIn1();Object.prototype.y=2;addReportExprJson("forIn1()","['x', 'y']");delete Object.prototype.y;function forIn2(){var result=[];var o={x:1,__proto__:null};for(var p in o)result.push(p);return result}forIn2();addReportExprJson("forIn2()","['x']");function forIn3(proto){var result=[];var o={x:1,__proto__:proto};for(var p in o)result.push(p);return result}forIn3({__proto__:{y1:2}});forIn3({__proto__:{y1:2}});addReportExprJson("forIn3({ __proto__: { y1: 2 } })","['x', 'y1']");forIn3({y2:2,__proto__:null});forIn3({y2:2,__proto__:null});addReportExprJson("forIn3({ y2 : 2, __proto__: null })","['x', 'y2']");forIn3({__proto__:{__proto__:{y3:2}}});forIn3({__proto__:{__proto__:{y3:2}}});addReportExprJson("forIn3({ __proto__: { __proto__: { y3 : 2 } } })","['x', 'y3']");function forIn4(o){var result=[];for(var p in o)result.push(p);return result}var objectWithArrayAsProto={};objectWithArrayAsProto.__proto__=[];addReportExprJson("forIn4(objectWithArrayAsProto)","[]");objectWithArrayAsProto.__proto__[0]=1;addReportExprJson("forIn4(objectWithArrayAsProto)","['0']");function forIn5(o){for(var i in o)return[i,o[i]]}addReportExprJson("forIn5({get foo() { return 'called getter'} })","['foo', 'called getter']");addReportExprJson("forIn5({set foo(v) { } })","['foo', undefined]");addReportExprJson("forIn5({get foo() { return 'called getter'}, set foo(v) { }})","['foo', 'called getter']");function cacheClearing(){for(var j=0;j<10;j++){var o={a:1,b:2,c:3,d:4,e:5};try{for(i in o){delete o.a;o=null;throw""}}finally{continue}}}cacheClearing();return RESULT