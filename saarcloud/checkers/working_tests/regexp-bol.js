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



var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}var s="abc123def456xyzabc789abc999";addReportExpr("s.match(/^notHere/)");addReportExprJson("s.match(/^abc/)",'["abc"]');addReportExprJson("s.match(/(^|X)abc/)",'["abc",""]');addReportExprJson("s.match(/^longer|123/)",'["123"]');addReportExprJson("s.match(/(^abc|c)123/)",'["abc123","abc"]');addReportExprJson("s.match(/(c|^abc)123/)",'["abc123","abc"]');addReportExprJson("s.match(/(^ab|abc)123/)",'["abc123","abc"]');addReportExprJson("s.match(/(bc|^abc)([0-9]*)a/)",'["bc789a","bc","789"]');addReportExpr('/(?:(Y)X)|(X)/.exec("abc")');addReportExpr('/(?:(?:^|Y)X)|(X)/.exec("abc")');addReportExpr('/(?:(?:^|Y)X)|(X)/.exec("abcd")');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("Xabcd")','["X",undefined]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("aXbcd")','["X","X"]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abXcd")','["X","X"]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abcXd")','["X","X"]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abcdX")','["X","X"]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("YXabcd")','["YX",undefined]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("aYXbcd")','["YX",undefined]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abYXcd")','["YX",undefined]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abcYXd")','["YX",undefined]');addReportExprJson('/(?:(?:^|Y)X)|(X)/.exec("abcdYX")','["YX",undefined]');return RESULT