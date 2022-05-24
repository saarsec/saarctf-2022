
var COLLECTED_RESULTS = [];
var EXPECTED_RESULTS = [];

function clone(cloneInputArg) { return JSON.parse(JSON.stringify(cloneInputArg)); }

function shouldBeTrue(expr) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push(clone(shouldBeInternalResult));
    EXPECTED_RESULTS.push(true);
}

function shouldBeFalse(expr) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push(clone(shouldBeInternalResult));
    EXPECTED_RESULTS.push(false);
}

function shouldBeNull(expr) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push(clone(shouldBeInternalResult));
    EXPECTED_RESULTS.push(null);
}

function shouldBeUndefined(expr) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push('' + shouldBeInternalResult);
    EXPECTED_RESULTS.push('undefined');
}

function shouldBeNaN(expr) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push('' + shouldBeInternalResult);
    EXPECTED_RESULTS.push('NaN');
}

function shouldBeEqualToString(expr, expected) {
    let shouldBeInternalResult = eval(expr);
    COLLECTED_RESULTS.push(JSON.stringify(shouldBeInternalResult));
    EXPECTED_RESULTS.push(JSON.stringify(expected));
}

function shouldBe(expr, expectedExpr) {
    let shouldBeInternalResult = eval(expr);
    let shouldBeInternalResult2 = eval(expectedExpr);
    COLLECTED_RESULTS.push(JSON.stringify(shouldBeInternalResult));
    EXPECTED_RESULTS.push(JSON.stringify(shouldBeInternalResult2));
    /*if (result != result2) {
        console.error('ERROR:', expr, result, JSON.stringify(result), '!=', expectedExpr, result2, JSON.stringify(result2));
    }*/
}

function shouldThrow(expr) {
    try {
        COLLECTED_RESULTS.push(JSON.stringify(eval(expr)));
        EXPECTED_RESULTS.push("<some expection>");
    } catch (e) {
        COLLECTED_RESULTS.push(e.toString());
        EXPECTED_RESULTS.push(e.toString());
    }
}

function shouldNotThrow(expr) {
    try {
        let shouldInternal = JSON.stringify(eval(expr));
        COLLECTED_RESULTS.push(shouldInternal);
        EXPECTED_RESULTS.push(shouldInternal);
    } catch (e) {
        COLLECTED_RESULTS.push(e.toString());
        EXPECTED_RESULTS.push(JSON.stringify(undefined));
    }
}

function doReportAfterTestsHaveRun() {
    console.log("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n" + JSON.stringify([COLLECTED_RESULTS, EXPECTED_RESULTS]));
}

function testPassed(){}
