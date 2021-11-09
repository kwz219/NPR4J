from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL,COMMIT_COL
from Utils.IOHelper import writeD2J
"""
get all information of a buggy-fix method
"""
def get_Minfo_all(M_signatures:list):
    mongoClient=MongoHelper()
    commit_col=mongoClient.get_col(COMMIT_COL)
    minfo_col=mongoClient.get_col(METHOD_COL)
    bug_col=mongoClient.get_col(BUG_COL)

    for ms in M_signatures:
        minfo=minfo_col.find_one({"_id":ms})
        buginfo=bug_col.find_one({"parent_id":ms})
        commit=minfo["commitID"]
        commitinfo=commit_col.find_one({"_id":commit})
        final_dict=refactor_buginfo(minfo,buginfo,commitinfo)
        return final_dict

"""
Organize bug information into a dict
---- _id
---- commit_info
     ---- repo
     ---- commit_url
     ---- commit_message
---- method_info
     ---- name
     ---- buggy
          --parent_file
          --start_line
          --end_line
          --code
     ---- fix
          --parent_file
          --start_line
          --end_line
          --code
---- bugfix_info
     ---- bug_nums
     ---- edit_types
     ---- bugfix_contents
          --list[errs]
            --err
              --type
              --src_pos(relative to buggy method)
              --tgt_pos(relative to  fix method)
              --src_content
              --tgt_content
"""
def refactor_buginfo(minfo:dict,buginfo:dict,commitinfo:dict):
    allinfo={}
    allinfo["id"]=minfo["_id"]
    allinfo["commit_info"]={"repo":commitinfo["repo"],
                            "commit_url:":commitinfo["commitURL"],
                            "commit_message":commitinfo["message"]}
    allinfo["method_info"]={"name":minfo["methodname"],
                            "buggy":{
                                "parent_file":minfo["buggy_file"],
                                "start_line":minfo["BLine_buggy"],
                                "end_line":minfo["ELine_buggy"],
                                "code":buginfo["buggy_code"]
                            },
                            "fix":{
                                "parent_file": minfo["fix_file"],
                                "start_line": minfo["Bline_fix"],
                                "end_line": minfo["Eline_fix"],
                                "code":buginfo["fix_code"]
                            }}
    allinfo['bugfix_info']={
        "bug_nums":buginfo["num_errs"],
        "edit_types":buginfo["type_errs"],
        "bugfix_contents":buginfo['errs']

    }
    return allinfo

def test_get_Minfo_all():
    sigs=[r"0000a9af91676cde100cdff6ca8de9bda8cb272d\P_dir\src\moe\xing\databindingformatter\WriterUtil.java@private void addMethod(PsiField field)"]
    final_dict=get_Minfo_all(sigs)
    writeD2J(final_dict,"test.json")

