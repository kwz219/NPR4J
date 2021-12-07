from Utils.CA_Utils import remove_comments
"""
implement data preprocess method of CoCoNut 
context_code and buggy_line as inputs, fix_line as labels
context_code: CoCoNut code of buggy method
buggy_line: the code line with bug
fix_line: the code line after fixing
"""
def run_CoCoNut_abs(buggy_code:str,buggy_line:str,fix_line:str):
    context_code=remove_comments(buggy_code)
    return context_code,buggy_line.strip(),fix_line.strip()

def test_CoCoNut_abs():
    buggycode="   public boolean UpdateAvailable(String url, float currVersion) {\n //initialize a\n boolean a = false;\nif (getNewVersion(url) > currVersion) {\na = true;\n}\nreturn a;\n}"
    buggy_line=" if (getNewVersion(url) > currVersion) {"
    fix_line="        if (Update.getNewVersion(url) > currVersion) {"
    print(run_CoCoNut_abs(buggycode,buggy_line,fix_line))

test_CoCoNut_abs()