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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}function multTest(){var x=1;x*=eval("2");return 2==x}function divTest(){var x=2;x/=eval("2");return 1==x}function addTest(){var x=0;x+=eval("1");return 1==x}function subTest(){var x=0;x-=eval("1");return-1==x}function lshiftTest(){var x=1;x<<=eval("1");return 2==x}function rshiftTest(){var x=1;x>>=eval("1");return 0==x}function urshiftTest(){var x=1;x>>>=eval("1");return 0==x}function andTest(){var x=1;x&=eval("1");return 1==x}function xorTest(){var x=0;x^=eval("1");return 1==x}function orTest(){var x=0;x|=eval("1");return 1==x}function modTest(){var x=4;x%=eval("3");return 1==x}function preIncTest(){var x={value:0};++eval("x").value;return 1==x.value}function preDecTest(){var x={value:0};--eval("x").value;return-1==x.value}function postIncTest(){var x={value:0};eval("x").value++;return 1==x.value}function postDecTest(){var x={value:0};eval("x").value--;return-1==x.value}function primitiveThisTest(){eval('this.value = "Seekrit message";');return"Seekrit message"===eval("this.value")}function strictThisTest(){"use strict";eval('this.value = "Seekrit message";');return void 0===eval("this.value")}addReportExpr("multTest();");addReportExpr("divTest();");addReportExpr("addTest();");addReportExpr("subTest();");addReportExpr("lshiftTest();");addReportExpr("rshiftTest();");addReportExpr("urshiftTest();");addReportExpr("andTest();");addReportExpr("xorTest();");addReportExpr("orTest();");addReportExpr("modTest();");addReportExpr("preIncTest();");addReportExpr("preDecTest();");addReportExpr("postIncTest();");addReportExpr("postDecTest();");addReportExpr("primitiveThisTest.call(1);");addExceptionExpr("strictThisTest.call(1);");return RESULT