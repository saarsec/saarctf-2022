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



var RESULT=[];function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function isKeyword(x){try{eval("var "+x+";")}catch(e){return true}return false}function isStrictKeyword(x){try{eval("'use strict'; var "+x+";")}catch(e){return true}return false}function classifyIdentifier(x){if(isKeyword(x)){if(!isStrictKeyword(x))return"ERROR";return"keyword"}if(isStrictKeyword(x))return"strict";return"identifier"}addReportExprJson('classifyIdentifier("x")','"identifier"');addReportExprJson('classifyIdentifier("id")','"identifier"');addReportExprJson('classifyIdentifier("identifier")','"identifier"');addReportExprJson('classifyIdentifier("keyword")','"identifier"');addReportExprJson('classifyIdentifier("strict")','"identifier"');addReportExprJson('classifyIdentifier("use")','"identifier"');addReportExprJson('classifyIdentifier("abstract")','"identifier"');addReportExprJson('classifyIdentifier("boolean")','"identifier"');addReportExprJson('classifyIdentifier("byte")','"identifier"');addReportExprJson('classifyIdentifier("char")','"identifier"');addReportExprJson('classifyIdentifier("double")','"identifier"');addReportExprJson('classifyIdentifier("final")','"identifier"');addReportExprJson('classifyIdentifier("float")','"identifier"');addReportExprJson('classifyIdentifier("goto")','"identifier"');addReportExprJson('classifyIdentifier("int")','"identifier"');addReportExprJson('classifyIdentifier("long")','"identifier"');addReportExprJson('classifyIdentifier("native")','"identifier"');addReportExprJson('classifyIdentifier("short")','"identifier"');addReportExprJson('classifyIdentifier("synchronized")','"identifier"');addReportExprJson('classifyIdentifier("throws")','"identifier"');addReportExprJson('classifyIdentifier("transient")','"identifier"');addReportExprJson('classifyIdentifier("volatile")','"identifier"');addReportExprJson('classifyIdentifier("break")','"keyword"');addReportExprJson('classifyIdentifier("case")','"keyword"');addReportExprJson('classifyIdentifier("catch")','"keyword"');addReportExprJson('classifyIdentifier("continue")','"keyword"');addReportExprJson('classifyIdentifier("debugger")','"keyword"');addReportExprJson('classifyIdentifier("default")','"keyword"');addReportExprJson('classifyIdentifier("delete")','"keyword"');addReportExprJson('classifyIdentifier("do")','"keyword"');addReportExprJson('classifyIdentifier("else")','"keyword"');addReportExprJson('classifyIdentifier("finally")','"keyword"');addReportExprJson('classifyIdentifier("for")','"keyword"');addReportExprJson('classifyIdentifier("function")','"keyword"');addReportExprJson('classifyIdentifier("if")','"keyword"');addReportExprJson('classifyIdentifier("in")','"keyword"');addReportExprJson('classifyIdentifier("instanceof")','"keyword"');addReportExprJson('classifyIdentifier("new")','"keyword"');addReportExprJson('classifyIdentifier("return")','"keyword"');addReportExprJson('classifyIdentifier("switch")','"keyword"');addReportExprJson('classifyIdentifier("this")','"keyword"');addReportExprJson('classifyIdentifier("throw")','"keyword"');addReportExprJson('classifyIdentifier("try")','"keyword"');addReportExprJson('classifyIdentifier("typeof")','"keyword"');addReportExprJson('classifyIdentifier("var")','"keyword"');addReportExprJson('classifyIdentifier("void")','"keyword"');addReportExprJson('classifyIdentifier("while")','"keyword"');addReportExprJson('classifyIdentifier("with")','"keyword"');addReportExprJson('classifyIdentifier("class")','"keyword"');addReportExprJson('classifyIdentifier("const")','"keyword"');addReportExprJson('classifyIdentifier("enum")','"keyword"');addReportExprJson('classifyIdentifier("export")','"keyword"');addReportExprJson('classifyIdentifier("extends")','"keyword"');addReportExprJson('classifyIdentifier("import")','"keyword"');addReportExprJson('classifyIdentifier("super")','"keyword"');addReportExprJson('classifyIdentifier("implements")','"strict"');addReportExprJson('classifyIdentifier("interface")','"strict"');addReportExprJson('classifyIdentifier("let")','"strict"');addReportExprJson('classifyIdentifier("package")','"strict"');addReportExprJson('classifyIdentifier("private")','"strict"');addReportExprJson('classifyIdentifier("protected")','"strict"');addReportExprJson('classifyIdentifier("public")','"strict"');addReportExprJson('classifyIdentifier("static")','"strict"');addReportExprJson('classifyIdentifier("yield")','"strict"');return RESULT