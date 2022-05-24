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



var RESULT=[];function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}var testObj={0:"a",1:"b",2:"c"};var lengthGetter={get:function(){throw true}};Object.defineProperty(testObj,"length",lengthGetter);function test(f){try{f.call(testObj,void 0);return false}catch(e){return true===e}}addReportExpr("test(Array.prototype.join)");addReportExpr("test(Array.prototype.pop)");addReportExpr("test(Array.prototype.push)");addReportExpr("test(Array.prototype.reverse)");addReportExpr("test(Array.prototype.shift)");addReportExpr("test(Array.prototype.slice)");addReportExpr("test(Array.prototype.sort)");addReportExpr("test(Array.prototype.splice)");addReportExpr("test(Array.prototype.unshift)");addReportExpr("test(Array.prototype.indexOf)");addReportExpr("test(Array.prototype.lastIndexOf)");addReportExpr("test(Array.prototype.every)");addReportExpr("test(Array.prototype.some)");addReportExpr("test(Array.prototype.forEach)");addReportExpr("test(Array.prototype.map)");addReportExpr("test(Array.prototype.filter)");addReportExpr("test(Array.prototype.reduce)");addReportExpr("test(Array.prototype.reduceRight)");return RESULT