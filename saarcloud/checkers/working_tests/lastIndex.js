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



// lastIndex is not configurable
var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}addReportExpr("delete /x/.lastIndex");addExceptionExpr("'use strict'; delete /x/.lastIndex");addReportExpr("'lastIndex' in /x/");addReportExpr("for (property in /x/) if (property === 'lastIndex') throw false; true");addReportExpr("var re = /x/; re.lastIndex = re; re.lastIndex === re");addExceptionExpr("Object.defineProperty(/x/, {get:function(){}})");addExceptionExpr("Object.defineProperty(/x/, 'lastIndex', {enumerable:true}); true");addReportExpr("Object.defineProperty(/x/, 'lastIndex', {enumerable:false}); true");addExceptionExpr("Object.defineProperty(/x/, 'lastIndex', {configurable:true}); true");addReportExpr("Object.defineProperty(/x/, 'lastIndex', {configurable:false}); true");addReportExprJson("var re = Object.defineProperty(/x/, 'lastIndex', {writable:true}); re.lastIndex = 42; re.lastIndex","42");addReportExprJson("var re = Object.defineProperty(/x/, 'lastIndex', {writable:false}); re.lastIndex = 42; re.lastIndex","0");addReportExprJson("var re = Object.defineProperty(/x/, 'lastIndex', {value:42}); re.lastIndex","42");addExceptionExpr("Object.defineProperty(Object.defineProperty(/x/, 'lastIndex', {writable:false}), 'lastIndex', {writable:true}); true");addExceptionExpr("Object.defineProperty(Object.defineProperty(/x/, 'lastIndex', {writable:false}), 'lastIndex', {value:42}); true");addReportExpr("Object.defineProperty(Object.defineProperty(/x/, 'lastIndex', {writable:false}), 'lastIndex', {value:0}); true");addReportExprJson("Object.defineProperty(/x/, 'lastIndex', {writable:false}).exec('')","null");addReportExprJson("Object.defineProperty(/x/, 'lastIndex', {writable:false}).exec('x')",'["x"]');addExceptionExpr("Object.defineProperty(/x/g, 'lastIndex', {writable:false}).exec('')");addExceptionExpr("Object.defineProperty(/x/g, 'lastIndex', {writable:false}).exec('x')");addReportExpr("var re = /x/; Object.freeze(re); Object.isFrozen(re);");return RESULT