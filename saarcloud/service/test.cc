#define TEST_PROGRAM
#include "jsengine/JSExecutionEngine.h"

int main() {
	auto te = JSThreadEngineGen.getEngine();
	auto engine1 = te->getSiteEngine(te, "test1");
	auto engine2 = te->getSiteEngine(te, "test2");
	engine1->runScriptFromExternal(readFile("../test1.js"), "test1.js");
	engine2->runScriptFromExternal(readFile("../test2.js"), "test2.js");
	return 0;
}
