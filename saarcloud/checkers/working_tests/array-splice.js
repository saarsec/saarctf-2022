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



var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}var arr=["a","b","c","d"];addReportExprJson("arr","['a','b','c','d']");addReportExprJson("arr.splice(2)","['c','d']");addReportExprJson("arr","['a','b']");addReportExprJson("arr.splice(0)","['a','b']");addReportExprJson("arr","[]");arr=["a","b","c","d"];addReportExprJson("arr.splice()","[]");addReportExprJson("arr","['a','b','c','d']");addReportExprJson("arr.splice(undefined)","['a','b','c','d']");addReportExprJson("arr","[]");arr=["a","b","c","d"];addReportExprJson("arr.splice(null)","['a','b','c','d']");addReportExprJson("arr","[]");arr=["a","b","c","d"];addReportExprJson("arr.splice(100)","[]");addReportExprJson("arr","['a','b','c','d']");addReportExprJson("arr.splice(-1)","['d']");addReportExprJson("arr","['a','b','c']");addReportExprJson("arr.splice(2, undefined)","[]");addReportExprJson("arr.splice(2, null)","[]");addReportExprJson("arr.splice(2, -1)","[]");addReportExprJson("arr","['a','b','c']");addReportExprJson("arr.splice(2, 100)","['c']");addReportExprJson("arr","['a','b']");return RESULT