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



var RESULT=[];function addExceptionExpr(expr){try{RESULT.push(JSON.stringify(eval(expr)))}catch(e){RESULT.push(e.toString())}}function addReportExprJson(expr){RESULT.push(JSON.stringify(eval(expr)))}function addReportExpr(expr){RESULT.push(JSON.parse(JSON.stringify(eval(expr))))}addExceptionExpr("Object.create()");addExceptionExpr("Object.create('a string')");addExceptionExpr("Object.create({}, 'a string')");addExceptionExpr("Object.create(null, 'a string')");addReportExprJson("JSON.stringify(Object.create(null,{property:{value:'foo', enumerable:true}, property2:{value:'foo', enumerable:true}}))",'\'{"property":"foo","property2":"foo"}\'');addReportExprJson("JSON.stringify(Object.create({},{property:{value:'foo', enumerable:true}, property2:{value:'foo', enumerable:true}}))",'\'{"property":"foo","property2":"foo"}\'');addReportExprJson("JSON.stringify(Object.create({},{property:{value:'foo'}, property2:{value:'foo', enumerable:true}}))",'\'{"property2":"foo"}\'');addReportExprJson("JSON.stringify(Object.create(null,{property:{value:'foo'}, property2:{value:'foo', enumerable:true}}))",'\'{"property2":"foo"}\'');addReportExprJson("Object.getPrototypeOf(Object.create(Array.prototype))","Array.prototype");addReportExprJson("Object.getPrototypeOf(Object.create(null))","null");function valueGet(){return true}var DescriptorWithValueGetter={foo:Object.create(null,{value:{get:valueGet}})};var DescriptorWithEnumerableGetter={foo:Object.create(null,{value:{value:true},enumerable:{get:valueGet}})};var DescriptorWithConfigurableGetter={foo:Object.create(null,{value:{value:true},configurable:{get:valueGet}})};var DescriptorWithWritableGetter={foo:Object.create(null,{value:{value:true},writable:{get:valueGet}})};var DescriptorWithGetGetter={foo:Object.create(null,{get:{get:function(){return valueGet}}})};var DescriptorWithSetGetter={foo:Object.create(null,{get:{value:valueGet},set:{get:function(){return valueGet}}})};addReportExpr("Object.create(null, DescriptorWithValueGetter).foo");addReportExpr("Object.create(null, DescriptorWithEnumerableGetter).foo");addReportExpr("Object.create(null, DescriptorWithConfigurableGetter).foo");addReportExpr("Object.create(null, DescriptorWithWritableGetter).foo");addReportExpr("Object.create(null, DescriptorWithGetGetter).foo");addReportExpr("Object.create(null, DescriptorWithSetGetter).foo");return RESULT