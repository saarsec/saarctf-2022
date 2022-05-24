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



// Simple hex & dec integer values.
var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}addReportExprJson("parseInt('123')","123");addReportExprJson("parseInt('123x4')","123");addReportExprJson("parseInt('-123')","-123");addReportExprJson("parseInt('0x123')","0x123");addReportExprJson("parseInt('0x123x4')","0x123");addReportExprJson("parseInt('-0x123x4')","-0x123");addReportExprJson("parseInt('-')","Number.NaN");addReportExprJson("parseInt('0x')","Number.NaN");addReportExprJson("parseInt('-0x')","Number.NaN");addReportExprJson("parseInt('123', undefined)","123");addReportExprJson("parseInt('123', null)","123");addReportExprJson("parseInt('123', 0)","123");addReportExprJson("parseInt('123', 10)","123");addReportExprJson("parseInt('123', 16)","0x123");addReportExprJson("parseInt('0x123', undefined)","0x123");addReportExprJson("parseInt('0x123', null)","0x123");addReportExprJson("parseInt('0x123', 0)","0x123");addReportExprJson("parseInt('0x123', 10)","0");addReportExprJson("parseInt('0x123', 16)","0x123");addReportExprJson("parseInt(Math.pow(10, 20))","100000000000000000000");addReportExprJson("parseInt(Math.pow(10, 21))","1");addReportExprJson("parseInt(Math.pow(10, -6))","0");addReportExprJson("parseInt(Math.pow(10, -7))","1");addReportExprJson("parseInt(-Math.pow(10, 20))","-100000000000000000000");addReportExprJson("parseInt(-Math.pow(10, 21))","-1");addReportExprJson("parseInt(-Math.pow(10, -6))","-0");addReportExprJson("parseInt(-Math.pow(10, -7))","-1");addReportExprJson("parseInt('0')","0");addReportExprJson("parseInt('-0')","-0");addReportExprJson("parseInt(0)","0");addReportExprJson("parseInt(-0)","0");addReportExprJson("parseInt(2147483647)","2147483647");addReportExprJson("parseInt(2147483648)","2147483648");addReportExprJson("parseInt('2147483647')","2147483647");addReportExprJson("parseInt('2147483648')","2147483648");var state;var throwingRadix={valueOf:function(){state="throwingRadix";throw null}};var throwingString={toString:function(){state="throwingString";throw null}};addReportExprJson("state = null; try { parseInt('123', throwingRadix); } catch (e) {} state;",'"throwingRadix"');addReportExprJson("state = null; try { parseInt(throwingString, throwingRadix); } catch (e) {} state;",'"throwingString"');return RESULT