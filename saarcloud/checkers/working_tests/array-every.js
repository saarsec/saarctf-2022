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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}function isBigEnough(element,index,array){return element>=10}addReportExpr("[12, 5, 8, 130, 44].every(isBigEnough)");addReportExpr("[12, 54, 18, 130, 44].every(isBigEnough)");var predicate={comparison:11,isBigEnough:function(s){return s>=comparison}};addReportExpr("[12, 5, 10, 130, 44].every(isBigEnough, predicate)");addReportExpr("[12, 54, 18, 130, 44].every(isBigEnough, predicate)");function isBigEnoughAndPop(element,index,array){array.pop();return element>=10}addReportExpr("[12, 5, 8, 130, 44].every(isBigEnoughAndPop)");addReportExpr("[12, 54, 18, 130, 44].every(isBigEnoughAndPop)");function isBigEnoughAndChange(element,index,array){array[array.length-1-index]=5;return element>=10}addReportExpr("[12, 5, 8, 130, 44].every(isBigEnoughAndChange)");addReportExpr("[12, 54, 18, 130, 44].every(isBigEnoughAndChange)");function isBigEnoughAndPush(element,index,array){array.push(131);return element>=131}addReportExpr("[12, 5, 8, 130, 44].every(isBigEnoughAndPush)");addReportExpr("[12, 54, 18, 130, 44].every(isBigEnoughAndPush)");function isBigEnoughAndException(element,index,array){if(1==index)throw"exception from function";return element>=10}addExceptionExpr("[12, 5, 8, 130, 44].every(isBigEnoughAndException)",'"exception from function"');addExceptionExpr("[12, 54, 18, 130, 44].every(isBigEnoughAndException)",'"exception from function"');addExceptionExpr("[12, 5, 8, 130, 44].every(5)");addExceptionExpr("[12, 5, 8, 130, 44].every('wrong')");addExceptionExpr("[12, 5, 8, 130, 44].every(new Object())");addExceptionExpr("[12, 5, 8, 130, 44].every(null)");addExceptionExpr("[12, 5, 8, 130, 44].every(undefined)");addExceptionExpr("[12, 5, 8, 130, 44].every()");var accumulator=new Array;function isBigEnoughShortCircuit(element,index,array){accumulator.push(element);return element>=10}addReportExpr("[12, 5, 8, 130, 44].every(isBigEnoughShortCircuit)");addReportExprJson("accumulator.toString()","[12, 5].toString()");accumulator.length=0;addReportExpr("[12, 54, 18, 130, 44].every(isBigEnoughShortCircuit)");addReportExprJson("accumulator.toString()","[12, 54, 18, 130, 44].toString()");var arr=[5,5,5,5];delete arr[1];function isNotUndefined(element,index,array){return"undefined"!==typeof element}addReportExpr("arr.every(isNotUndefined)");arr=new Array(20);addReportExpr("arr.every(isNotUndefined)");return RESULT