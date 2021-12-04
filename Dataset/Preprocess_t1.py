# -*- coding : utf-8-*-
from bson import ObjectId
from MongoHelper import MongoHelper
from DataConstants import BUG_COL, METHOD_COL
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from Utils.IOHelper import writeL2F, readF2L
import os


def preprocess(ids: list, method, input_dir, output_dir):
    mongoClient = MongoHelper()
    bug_col = mongoClient.get_col(BUG_COL)
    if method == "SequenceR":
        def build(src_f, tgt_f, error_f, correct_f, ids):
            buggy_codes = []
            fix_codes = []
            error_ids = []
            correct_ids = []
            ind = 1
            for id in ids:
                bug = bug_col.find_one({"_id": ObjectId(id)})
                buggy_parent_f = bug['parent_id'].split("@")[0]
                tmp_f = "D:\DDPR_TEST\SR_AB\\val_tmp\\" + buggy_parent_f.split("\\")[0] + "_" + \
                        buggy_parent_f.split("\\")[-1]
                fix_code = ''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()
                # print(buggy_parent_f,tmp_f)

                buggy_code, hitflag = run_SequenceR_abs(input_dir + buggy_parent_f, tmp_f, bug)

                if hitflag == 1:
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    correct_ids.append(bug['_id'])
                else:
                    error_ids.append(bug['_id'])
                print(ind)
                ind += 1

            writeL2F(buggy_codes, src_f)
            writeL2F(fix_codes, tgt_f)
            writeL2F(error_ids, error_f)
            writeL2F(correct_ids, correct_f)

        build(output_dir + "val.buggy_1", output_dir + "val.fix_1", output_dir + "val.fids_1",
              output_dir + "val.sids_1", ids)
        # build(output_dir+"buggy.val.txt",output_dir+"fix.val.txt",output_dir+"error_ids.val.txt",output_dir+"correct_ids.val.txt",val_ids)


def test_preprocess():
    val_ids = readF2L("D:\DDPR\Dataset\\freq50_611\\val_ids.txt")
    preprocess(val_ids[10000:20000], "SequenceR", "E:\\bug-fix\\", "D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")


test_preprocess()