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



// Regression test for <rdar://problem/10763509>


var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function callee(a1,a2,a3,a4,a5,a6,a7,a8){if(void 0!==a1)return"Arg1 is wrong";if(void 0!==a2)return"Arg2 is wrong";if(void 0!==a3)return"Arg3 is wrong";if(void 0!==a4)return"Arg4 is wrong";if(void 0!==a5)return"Arg5 is wrong";if(void 0!==a6)return"Arg6 is wrong";if(void 0!==a7)return"Arg7 is wrong";if(void 0!==a8)return"Arg8 is wrong";return}function dummy(a1,a2,a3,a4,a5,a6,a7,a8){}function BaseObj(){}function caller(testArgCount){var baseObj=new BaseObj;var allArgs=[0,"String",callee,true,null,2.5,[1,2,3],{a:1,b:2}];argCounts=[8,testArgCount];for(argCountIndex=0;argCountIndex<argCounts.length;argCountIndex++){argCount=argCounts[argCountIndex];var varArgs=[];for(i=0;i<argCount;i++)varArgs[i]=void 0;for(numCalls=0;numCalls<10;numCalls++){dummy.apply(baseObj,allArgs);var result=callee.apply(baseObj,varArgs);if(void 0!=result)return result}}return}addReportExprJson("caller(0)","undefined");addReportExprJson("caller(1)","undefined");addReportExprJson("caller(2)","undefined");addReportExprJson("caller(3)","undefined");addReportExprJson("caller(4)","undefined");addReportExprJson("caller(5)","undefined");addReportExprJson("caller(6)","undefined");addReportExprJson("caller(7)","undefined");addReportExprJson("caller(8)","undefined");var successfullyParsed=true;return RESULT