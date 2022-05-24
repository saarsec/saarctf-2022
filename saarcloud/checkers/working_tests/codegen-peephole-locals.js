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



var RESULT=[];function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}function if_less_test(){var a=0;var b=2;if(a=1<2)return 1==a}addReportExpr("if_less_test()");function if_else_less_test(){var a=0;var b=2;if(a=1<2)return 1==a;else return false}addReportExpr("if_else_less_test()");function conditional_less_test(){var a=0;var b=2;return(a=1<2)?1==a:false}addReportExpr("conditional_less_test()");function logical_and_less_test(){var a=0;var b=2;return(a=1<2)&&1==a}addReportExpr("logical_and_less_test()");function logical_or_less_test(){var a=0;var b=2;var result=(a=1<2)||1==a;return 1==a}addReportExpr("logical_or_less_test()");function do_while_less_test(){var a=0;var count=0;do{if(1==count)return 1==a;count++}while(a=1<2)}addReportExpr("do_while_less_test()");function while_less_test(){var a=0;while(a=1<2)return 1==a}addReportExpr("while_less_test()");function for_less_test(){for(var a=0;a=1<2;)return 1==a}addReportExpr("for_less_test()");return RESULT