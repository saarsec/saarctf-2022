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



var RESULT = [];
function addReportExprJson(expr){ RESULT.push(JSON.stringify(eval(expr))); }
function addReportExpr(expr){ RESULT.push(JSON.parse(JSON.stringify(eval(expr)))); }
function testForwardSlash(pattern, _string)
{
    string = _string;

    re1 = new RegExp(pattern);
    re2 = eval(re1.toString());

    return re1.test(string) && re2.test(string);
}

function testLineTerminator(pattern)
{
    re1 = new RegExp(pattern);

    return /\n|\r|\u2028|\u2029/.test(re1.toString());
}

addReportExprJson("RegExp('/').source", '"\\\\/"');
addReportExprJson("RegExp('').source", '"(?:)"');
addReportExprJson("RegExp.prototype.source", '"(?:)"');

addReportExprJson("RegExp('/').toString()", '"/\\\\//"');
addReportExprJson("RegExp('').toString()", '"/(?:)/"');
addReportExprJson("RegExp.prototype.toString()", '"/(?:)/"');

// These strings are equivalent, since the '\' is identity escaping the '/' at the string level.
addReportExpr('testForwardSlash("^/$", "/");');
addReportExpr('testForwardSlash("^\/$", "/");');
// This string passes "^\/$" to the RegExp, so the '/' is escaped in the re!
addReportExpr('testForwardSlash("^\\/$", "/");');
// These strings pass "^\\/$" and "^\\\/$" respectively to the RegExp, giving one '\' to match.
addReportExpr('testForwardSlash("^\\\\/$", "\\/");');
addReportExpr('testForwardSlash("^\\\\\\/$", "\\/");');
// These strings match two backslashes (the second with the '/' escaped).
addReportExpr('testForwardSlash("^\\\\\\\\/$", "\\\\/");');
addReportExpr('testForwardSlash("^\\\\\\\\\\/$", "\\\\/");');
// Test that nothing goes wrongif there are multiple forward slashes!
addReportExpr('testForwardSlash("x/x/x", "x\\/x\\/x");');
addReportExpr('testForwardSlash("x\\/x/x", "x\\/x\\/x");');
addReportExpr('testForwardSlash("x/x\\/x", "x\\/x\\/x");');
addReportExpr('testForwardSlash("x\\/x\\/x", "x\\/x\\/x");');

addReportExpr('testLineTerminator("\\n");');
addReportExpr('testLineTerminator("\\\\n");');
addReportExpr('testLineTerminator("\\r");');
addReportExpr('testLineTerminator("\\\\r");');
addReportExpr('testLineTerminator("\\u2028");');
addReportExpr('testLineTerminator("\\\\u2028");');
addReportExpr('testLineTerminator("\\u2029");');
addReportExpr('testLineTerminator("\\\\u2029");');

addReportExprJson("RegExp('[/]').source", "'[/]'");
addReportExprJson("RegExp('\\\\[/]').source", "'\\\\[\\\\/]'");

// See 15.10.6.4
// The first half of this checks that:
//     Return the String value formed by concatenating the Strings "/", the
//     String value of the source property of this RegExp object, and "/";
// The second half checks that:
//     The returned String has the form of a RegularExpressionLiteral that
//     evaluates to another RegExp object with the same behaviour as this object.
addReportExprJson("var o = new RegExp(); o.toString() === '/'+o.source+'/' && eval(o.toString()+'.exec(String())')", '[""]');

return RESULT;