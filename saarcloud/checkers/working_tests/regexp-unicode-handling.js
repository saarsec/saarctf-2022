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



// Regex to match Re in various languanges straight from Gmail source
var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}var I3=/^\s*(fwd|re|aw|antw|antwort|wg|sv|ang|odp|betreff|betr|transf|reenv\.|reenv|in|res|resp|resp\.|enc|\u8f6c\u53d1|\u56DE\u590D|\u041F\u0435\u0440\u0435\u0441\u043B|\u041E\u0442\u0432\u0435\u0442):\s*(.*)$/i;var Ci=/\s+/g;var BC=/^ /;var BG=/ $/;function cy(a){var b=I3.exec(a);if(b)a=b[2];return Gn(a)}function Gn(a){return a.replace(Ci," ").replace(BC,"").replace(BG,"")}addReportExprJson("cy('Re: Moose')","'Moose'");addReportExprJson("cy('\\u8f6c\\u53d1: Moose')","'Moose'");var sample="sample bm⠠p cm\\u2820p";var inlineRe=/.m\u2820p/;var evalInlineRe=eval("/.m\\u2820p/");var explicitRe=new RegExp(".m\\u2820p");var newFromInlineRe=new RegExp(inlineRe.source);var evalFromInlineRe=eval(inlineRe.toString());var newFromEvalInlineRe=new RegExp(evalInlineRe.source);var evalFromEvalInlineRe=eval(evalInlineRe.toString());var newFromExplicitRe=new RegExp(explicitRe.source);var evalFromExplicitRe=eval(explicitRe.toString());addReportExprJson("inlineRe.source","newFromInlineRe.source");addReportExprJson("inlineRe.source","evalFromInlineRe.source");addReportExprJson("inlineRe.source","evalInlineRe.source");addReportExprJson("inlineRe.source","newFromEvalInlineRe.source");addReportExprJson("inlineRe.source","evalFromEvalInlineRe.source");addReportExprJson("inlineRe.source","explicitRe.source");addReportExprJson("inlineRe.source","newFromExplicitRe.source");addReportExprJson("inlineRe.source","evalFromExplicitRe.source");addReportExprJson("inlineRe.toString()","newFromInlineRe.toString()");addReportExprJson("inlineRe.toString()","evalFromInlineRe.toString()");addReportExprJson("inlineRe.toString()","evalInlineRe.toString()");addReportExprJson("inlineRe.toString()","newFromEvalInlineRe.toString()");addReportExprJson("inlineRe.toString()","evalFromEvalInlineRe.toString()");addReportExprJson("inlineRe.toString()","explicitRe.toString()");addReportExprJson("inlineRe.toString()","newFromExplicitRe.toString()");addReportExprJson("inlineRe.toString()","evalFromExplicitRe.toString()");addReportExprJson("inlineRe.exec(sample)[0]","'bm⠠p'");addReportExprJson("evalInlineRe.exec(sample)[0]","'bm⠠p'");addReportExprJson("explicitRe.exec(sample)[0]","'bm⠠p'");var bsample="sample bm|p cm\\u007cp";var binlineRe=/.m\u007cp/;var bevalInlineRe=eval("/.m\\u007cp/");var bexplicitRe=new RegExp(".m\\u007cp");var bnewFromInlineRe=new RegExp(binlineRe.source);var bevalFromInlineRe=eval(binlineRe.toString());var bnewFromEvalInlineRe=new RegExp(bevalInlineRe.source);var bevalFromEvalInlineRe=eval(bevalInlineRe.toString());var bnewFromExplicitRe=new RegExp(bexplicitRe.source);var bevalFromExplicitRe=eval(bexplicitRe.toString());addReportExprJson("binlineRe.source","bnewFromInlineRe.source");addReportExprJson("binlineRe.source","bevalFromInlineRe.source");addReportExprJson("binlineRe.source","bevalInlineRe.source");addReportExprJson("binlineRe.source","bnewFromEvalInlineRe.source");addReportExprJson("binlineRe.source","bevalFromEvalInlineRe.source");addReportExprJson("binlineRe.source","bexplicitRe.source");addReportExprJson("binlineRe.source","bnewFromExplicitRe.source");addReportExprJson("binlineRe.source","bevalFromExplicitRe.source");addReportExprJson("binlineRe.toString()","bnewFromInlineRe.toString()");addReportExprJson("binlineRe.toString()","bevalFromInlineRe.toString()");addReportExprJson("binlineRe.toString()","bevalInlineRe.toString()");addReportExprJson("binlineRe.toString()","bnewFromEvalInlineRe.toString()");addReportExprJson("binlineRe.toString()","bevalFromEvalInlineRe.toString()");addReportExprJson("binlineRe.toString()","bexplicitRe.toString()");addReportExprJson("binlineRe.toString()","bnewFromExplicitRe.toString()");addReportExprJson("binlineRe.toString()","bevalFromExplicitRe.toString()");addReportExprJson("binlineRe.exec(bsample)[0]","'bm|p'");addReportExprJson("bevalInlineRe.exec(bsample)[0]","'bm|p'");addReportExprJson("bexplicitRe.exec(bsample)[0]","'bm|p'");return RESULT