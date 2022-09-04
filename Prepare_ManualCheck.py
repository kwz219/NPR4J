import codecs
import json
import os

import pandas

from Utils.IOHelper import readF2L, readF2L_ori


def prepare_QuixBugs_for_check(quixbugs_info_f,patch_dir,sys,outout_dir):
    quixbug_infos=json.load(codecs.open(quixbugs_info_f,'r',encoding='utf8'))
    files=os.listdir(patch_dir)
    def get_pred_line(patch_f,sys):
        if not sys == "Tufano":
            patch_lines=readF2L_ori(patch_f)
            for line in patch_lines:
                if line.lstrip()==line:
                    return line
        else:
            patch_method=codecs.open(patch_f,'r',encoding='utf8').read().strip()
            return patch_method
        return "parse_error"
    tool_names=[]
    bug_names=[]
    buggy_lines=[]
    develop_patch_lines=[]
    patch_indexes=[]
    pred_lines=[]
    for file in files:
        if file.endswith(".patch"):
            infos=file.split("_")
            #tool_name=infos[0]
            tool_name=sys
            if len(infos)==4:
                bug_name=infos[1]
            else:
                bug_name="_".join(infos[1:-2])

                bug_name=bug_name.replace("ori_","")
            print(bug_name)
            patch_index=int(infos[-1].replace(".patch",''))
            pred_patch=get_pred_line(patch_dir+'/'+file,sys)
            buggy_line=quixbug_infos[bug_name]["buggy_line"]
            develop_patch_line=quixbug_infos[bug_name]["patch_line"]

            tool_names.append(tool_name)
            bug_names.append(bug_name)
            buggy_lines.append(buggy_line)
            develop_patch_lines.append(develop_patch_line)
            patch_indexes.append(patch_index)
            pred_lines.append(pred_patch)
    df=pandas.DataFrame({"Bug-Name":bug_names,"NPR-System":tool_names,"Buggy-Line":buggy_lines,"Develop-Patch-Line":develop_patch_lines,
                         "Patch-Index":patch_indexes,"Pred-Patch":pred_lines})
    df.to_excel(outout_dir+'/qbs_'+sys+'.xlsx')

#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/SequenceR",
                           #"SequenceR","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/CoCoNut",
                           #"CoCoNut","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/CodeBERT-ft",
                           #"CodeBERT-ft","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Edits",
                           #"Edits","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Recoder",
                           #"Recoder","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Recoder_ori",
                           #"Recoder_ori","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Tufano",
                           #"Tufano","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/RewardRepair",
                           #"RewardRepair","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/RewardRepair_ori",
                           #"RewardRepair_ori","D:/NPR4J-Eval-Results/manual_check")
def prepare_Bears_for_check(bears_info_f_1,bears_info_f_2,patch_dir,pred_f,sys,output_dir):
    bears_infos=json.load(codecs.open(bears_info_f_1,'r',encoding='utf8'))
    bears_prefix=json.load(codecs.open(bears_info_f_2,'r',encoding='utf8'))
    files = os.listdir(patch_dir)
    patches=json.load(codecs.open(pred_f,'r',encoding='utf8'))
    tool_names=[]
    bug_names=[]
    buggy_lines=[]
    develop_patch_lines=[]
    patch_indexes=[]
    pred_lines=[]
    sub_ids=[]
    for file in files:
        if "_right" in file:
            candidate_index=int(file.split('.')[-1])
            Bug_name=file.split("_")[-2]
            ids=list(bears_infos[Bug_name].keys())
            for id in ids:
                if id not in patches.keys():
                    break
                infos=bears_prefix[id]
                buggy_line=infos["buggy_line"]
                developer_line=infos["developer_line"]
                prefix=infos["prefix"]
                postfix=infos["postfix"]
                if str(candidate_index) not in patches[id].keys():
                    print(id,candidate_index)
                    break
                patch_method=patches[id][str(candidate_index)]
                prefix=prefix.strip()
                postfix=postfix.strip()
                if not sys in ["Recoder","Recoder_ori"]:
                    prefix=prefix.replace('\n','\n\n')
                    postfix = postfix.replace('\n','\n\n')
                if id in ["bears_6257cdb15fef470c3d70c26d"]:
                    postfix="long deviceId = findDeviceId(remoteAddress, uniqueIds);\n            if (deviceId != 0) {\n                if (Context.getConnectionManager() != null) {\n                    Context.getConnectionManager().addActiveDevice(deviceId, protocol, channel, remoteAddress);\n                }\n                return new DeviceSession(deviceId);\n            } else {\n                return null;\n            }\n        }\n        if (channel instanceof DatagramChannel) {\n            long deviceId = findDeviceId(remoteAddress, uniqueIds);\n            DeviceSession deviceSession = addressDeviceSessions.get(remoteAddress);\n            if (deviceSession != null && (deviceSession.getDeviceId() == deviceId || uniqueIds.length == 0)) {\n                return deviceSession;\n            } else if (deviceId != 0) {\n                deviceSession = new DeviceSession(deviceId);\n                addressDeviceSessions.put(remoteAddress, deviceSession);\n                if (Context.getConnectionManager() != null) {\n                    Context.getConnectionManager().addActiveDevice(deviceId, protocol, channel, remoteAddress);\n                }\n                return deviceSession;\n            } else {\n                return null;\n            }\n        } else {\n            if (channelDeviceSession == null) {\n                long deviceId = findDeviceId(remoteAddress, uniqueIds);\n                if (deviceId != 0) {\n                    channelDeviceSession = new DeviceSession(deviceId);\n                    if (Context.getConnectionManager() != null) {\n                        Context.getConnectionManager().addActiveDevice(deviceId, protocol, channel, remoteAddress);\n                    }\n                }\n            }\n            return channelDeviceSession;\n        }\n    }"
                #print(id)
                #print(postfix)
                try:
                    if sys not in ["Tufano"]:
                        assert prefix in  patch_method
                        assert postfix in patch_method
                    if sys in ["Tufano"]:
                        patch_line=patch_method.strip()
                    else:
                        patch_line = patch_method.replace(prefix, '', 1).replace(postfix, '').strip()
                    tool_names.append(sys)
                    bug_names.append(Bug_name)
                    buggy_lines.append(buggy_line)
                    develop_patch_lines.append(developer_line)
                    patch_indexes.append(candidate_index)
                    pred_lines.append(patch_line)
                    sub_ids.append(id)
                except:
                    print(id,candidate_index)



    df=pandas.DataFrame({"Bug-Name":bug_names,"Id":sub_ids,"NPR-System":tool_names,"Buggy-Line":buggy_lines,"Develop-Patch-Line":develop_patch_lines,
                         "Patch-Index":patch_indexes,"Pred-Patch":pred_lines})
    df.to_excel(output_dir+'/bears_'+sys+'.xlsx')
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/CoCoNut",pred_f=r"D:\NPR4J-Eval-Results\bears\CoCoNut\CoCoNut_300.patches",
                        #sys="CoCoNut",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/Edits",pred_f=r"D:\NPR4J-Eval-Results\bears\Edits\Edits_bears_b300.patches",
                        #sys="Edits",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/CodeBERT-ft",pred_f=r"D:\NPR4J-Eval-Results\bears\CodeBERT-ft\CodeBERT-ft_b300_bears.patches",
                        #sys="CodeBERT-ft",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/SequenceR",pred_f=r"D:\NPR4J-Eval-Results\bears\SequenceR\SequenceR_b300_bears.patches",
                        #sys="SequenceR",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/Recoder",pred_f=r"D:\NPR4J-Eval-Results\bears\Recoder\recoder.patches",
                        #sys="Recoder",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/Recoder_ori",pred_f=r"D:\NPR4J-Eval-Results\bears\Recoder_ori\recoder_ori_b300.patches",
                        #sys="Recoder_ori",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="D:/NPR4J-Eval-Results/bears/RewardRepair_ori",pred_f=r"D:\NPR4J-Eval-Results\bears\RewardRepair_ori\bears_ori.patches",
                        #sys="RewardRepair_ori",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/bears/NPR-Eval",pred_f=r"E:/NPR4J/ICSE23/NPR4J_Eval/bears/NPR-Eval/Tufano_b300_bears.patches",
                        #sys="Tufano",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_Bears_for_check(bears_info_f_1="Utils/Bears.json",bears_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/bears/RewardRepair",pred_f=r"E:/NPR4J/ICSE23/NPR4J_Eval/bears/RewardRepair/bears_mine.patches",
                        #sys="RewardRepair",output_dir="D:/NPR4J-Eval-Results/manual_check")
def prepare_d4j_for_check(d4j_info_f_1,d4j_info_f_2,patch_dir,pred_f,sys,output_dir):
    bug_ids=json.load(codecs.open(d4j_info_f_1,'r',encoding='utf8'))["d4j"]
    id_infos=json.load(codecs.open(d4j_info_f_2,'r',encoding='utf8'))
    files = os.listdir(patch_dir)
    patches = json.load(codecs.open(pred_f, 'r', encoding='utf8'))
    tool_names = []
    bug_names = []
    buggy_lines = []
    develop_patch_lines = []
    patch_indexes = []
    pred_lines = []
    sub_ids = []

    for file in files:
        if "_passed" in file:
            #print(file)
            ori_candidate_indexes = eval(file.split('_')[-2])
            candidate_indexes=[ind+1 for ind in ori_candidate_indexes]
            Bug_name = file.split("_")[1]+"_"+file.split("_")[2]
            ids=[]
            for key in bug_ids[Bug_name].keys():
                ids+=bug_ids[Bug_name][key]["ids"]


            assert len(candidate_indexes)==len(ids)
            for idx,id in enumerate(ids):
                if sys in ["Recoder_ori","RewardRepair","RewardRepair_ori","Tufano"]:
                    id="d4j_"+id

                if id not in patches.keys():

                    break

                infos = id_infos[id]
                buggy_line = infos["buggy_line"]
                developer_line = infos["developer_line"]
                prefix = infos["prefix"]
                postfix = infos["postfix"]
                if str(candidate_indexes[idx]) not in patches[id].keys():
                    print(id, candidate_indexes[idx])
                    break
                patch_method = patches[id][str(candidate_indexes[idx])]
                prefix = prefix.strip()
                postfix = postfix.strip()
                if not sys in ["Recoder", "Recoder_ori"]:
                    prefix = prefix.replace('\n', '\n\n')
                    postfix = postfix.replace('\n', '\n\n')
                # print(id)
                # print(postfix)
                prefix=prefix.replace('\r','')
                postfix=postfix.replace('\r','')
                if sys in ["Recoder","Recoder_ori"]:
                    if id == "61a8cca68009e7c4a5d3d7f6":
                        prefix_1="private String format(JSError error, boolean warning) {\n    // extract source excerpt\n    SourceExcerptProvider source = getSource();\n    String sourceExcerpt = source == null ? null :\n        excerpt.get(\n            source, error.sourceName, error.lineNumber, excerptFormatter);\n\n    // formatting the message\n    StringBuilder b = new StringBuilder();\n    if (error.sourceName != null) {\n      b.append(error.sourceName);\n      if (error.lineNumber > 0) {\n        b.append(':');\n        b.append(error.lineNumber);\n      }\n      b.append(\": \");\n    }\n\n    b.append(getLevelName(warning ? CheckLevel.WARNING : CheckLevel.ERROR));\n    b.append(\" - \");\n\n    b.append(error.description);\n    b.append('\\n');\n    if (sourceExcerpt != null) {\n      b.append(sourceExcerpt);\n      b.append('\\n');\n      int charno = error.getCharno();\n\n      // padding equal to the excerpt and arrow at the end\n      // charno == sourceExpert.length() means something is missing\n      // at the end of the line\nif(excerpt.equals(LINE)"
                        prefix_2="private String format(JSError error, boolean warning) {\n    // extract source excerpt\n    SourceExcerptProvider source = getSource();\n    String sourceExcerpt = source == null ? null :\n        excerpt.get(\n            source, error.sourceName, error.lineNumber, excerptFormatter);\n\n    // formatting the message\n    StringBuilder b = new StringBuilder();\n    if (error.sourceName != null) {\n      b.append(error.sourceName);\n      if (error.lineNumber > 0) {\n        b.append(':');\n        b.append(error.lineNumber);\n      }\n      b.append(\": \");\n    }\n\n    b.append(getLevelName(warning ? CheckLevel.WARNING : CheckLevel.ERROR));\n    b.append(\" - \");\n\n    b.append(error.description);\n    b.append('\\n');\n    if (sourceExcerpt != null) {\n      b.append(sourceExcerpt);\n      b.append('\\n');\n      int charno = error.getCharno();\n\n      // padding equal to the excerpt and arrow at the end\n      // charno == sourceExpert.length() means something is missing\n      // at the end of the line\nif((excerpt.equals(LINE)"
                        prefix_3="private String format(JSError error, boolean warning) {\n    // extract source excerpt\n    SourceExcerptProvider source = getSource();\n    String sourceExcerpt = source == null ? null :\n        excerpt.get(\n            source, error.sourceName, error.lineNumber, excerptFormatter);\n\n    // formatting the message\n    StringBuilder b = new StringBuilder();\n    if (error.sourceName != null) {\n      b.append(error.sourceName);\n      if (error.lineNumber > 0) {\n        b.append(':');\n        b.append(error.lineNumber);\n      }\n      b.append(\": \");\n    }\n\n    b.append(getLevelName(warning ? CheckLevel.WARNING : CheckLevel.ERROR));\n    b.append(\" - \");\n\n    b.append(error.description);\n    b.append('\\n');\n    if (sourceExcerpt != null) {\n      b.append(sourceExcerpt);\n      b.append('\\n');\n      int charno = error.getCharno();\n\n      // padding equal to the excerpt and arrow at the end\n      // charno == sourceExpert.length() means something is missing\n      // at the end of the line\nif(((excerpt.equals(LINE)"
                        prefix_4="private String format(JSError error, boolean warning) {\n    // extract source excerpt\n    SourceExcerptProvider source = getSource();\n    String sourceExcerpt = source == null ? null :\n        excerpt.get(\n            source, error.sourceName, error.lineNumber, excerptFormatter);\n\n    // formatting the message\n    StringBuilder b = new StringBuilder();\n    if (error.sourceName != null) {\n      b.append(error.sourceName);\n      if (error.lineNumber > 0) {\n        b.append(':');\n        b.append(error.lineNumber);\n      }\n      b.append(\": \");\n    }\n\n    b.append(getLevelName(warning ? CheckLevel.WARNING : CheckLevel.ERROR));\n    b.append(\" - \");\n\n    b.append(error.description);\n    b.append('\\n');\n    if (sourceExcerpt != null) {\n      b.append(sourceExcerpt);\n      b.append('\\n');\n      int charno = error.getCharno();\n\n      // padding equal to the excerpt and arrow at the end\n      // charno == sourceExpert.length() means something is missing\n      // at the end of the line\n"
                        prefix = prefix_1
                        if prefix not in patch_method:
                            prefix=prefix_2
                        if prefix not in patch_method:
                            prefix=prefix_3
                        if prefix not in patch_method:
                            prefix=prefix_4
                        postfix="for (int i = 0; i < charno; i++) {\n          char c = sourceExcerpt.charAt(i);\n          if (Character.isWhitespace(c)) {\n            b.append(c);\n          } else {\n            b.append(' ');\n          }\n        }\n        b.append(\"^\\n\");\n      }\n    }\n    return b.toString();\n  }"
                    elif id == "d4j_61a8cca68009e7c4a5d3d919":
                        prefix="protected Size2D arrangeFF(BlockContainer container, Graphics2D g2,\n                               RectangleConstraint constraint) {\n        double[] w = new double[5];\n        double[] h = new double[5];\n        w[0] = constraint.getWidth();\n        if (this.topBlock != null) {\n            RectangleConstraint c1 = new RectangleConstraint(w[0], null,\n                    LengthConstraintType.FIXED, 0.0,\n                    new Range(0.0, constraint.getHeight()),\n                    LengthConstraintType.RANGE);\n            Size2D size = this.topBlock.arrange(g2, c1);\n            h[0] = size.height;\n        }\n        w[1] = w[0];\n        if (this.bottomBlock != null) {\n            RectangleConstraint c2 = new RectangleConstraint(w[0], null,\n                    LengthConstraintType.FIXED, 0.0, new Range(0.0,\n                    constraint.getHeight() - h[0]), LengthConstraintType.RANGE);\n            Size2D size = this.bottomBlock.arrange(g2, c2);\n            h[1] = size.height;\n        }\n        h[2] = constraint.getHeight() - h[1] - h[0];\n        if (this.leftBlock != null) {\n            RectangleConstraint c3 = new RectangleConstraint(0.0,\n                    new Range(0.0, constraint.getWidth()),\n                    LengthConstraintType.RANGE, h[2], null,\n                    LengthConstraintType.FIXED);\n            Size2D size = this.leftBlock.arrange(g2, c3);\n            w[2] = size.width;\n        }\n        h[3] = h[2];\n        if (this.rightBlock != null) {\nRectangleConstraint c4 = new RectangleConstraint(0.0,"
                        postfix="LengthConstraintType.RANGE, h[2], null, LengthConstraintType.FIXED);\n            Size2D size = this.rightBlock.arrange(g2, c4);\n            w[3] = size.width;\n        }\n        h[4] = h[2];\n        w[4] = constraint.getWidth() - w[3] - w[2];\n        RectangleConstraint c5 = new RectangleConstraint(w[4], h[4]);\n        if (this.centerBlock != null) {\n            this.centerBlock.arrange(g2, c5);\n        }\n\n        if (this.topBlock != null) {\n            this.topBlock.setBounds(new Rectangle2D.Double(0.0, 0.0, w[0],\n                    h[0]));\n        }\n        if (this.bottomBlock != null) {\n            this.bottomBlock.setBounds(new Rectangle2D.Double(0.0, h[0] + h[2],\n                    w[1], h[1]));\n        }\n        if (this.leftBlock != null) {\n            this.leftBlock.setBounds(new Rectangle2D.Double(0.0, h[0], w[2],\n                    h[2]));\n        }\n        if (this.rightBlock != null) {\n            this.rightBlock.setBounds(new Rectangle2D.Double(w[2] + w[4], h[0],\n                    w[3], h[3]));\n        }\n        if (this.centerBlock != null) {\n            this.centerBlock.setBounds(new Rectangle2D.Double(w[2], h[0], w[4],\n                    h[4]));\n        }\n        return new Size2D(constraint.getWidth(), constraint.getHeight());\n    }"
                    elif id == "d4j_61a8cca68009e7c4a5d3d7f6":
                        prefix="private String format(JSError error, boolean warning) {\n    // extract source excerpt\n    SourceExcerptProvider source = getSource();\n    String sourceExcerpt = source == null ? null :\n        excerpt.get(\n            source, error.sourceName, error.lineNumber, excerptFormatter);\n\n    // formatting the message\n    StringBuilder b = new StringBuilder();\n    if (error.sourceName != null) {\n      b.append(error.sourceName);\n      if (error.lineNumber > 0) {\n        b.append(':');\n        b.append(error.lineNumber);\n      }\n      b.append(\": \");\n    }\n\n    b.append(getLevelName(warning ? CheckLevel.WARNING : CheckLevel.ERROR));\n    b.append(\" - \");\n\n    b.append(error.description);\n    b.append('\\n');\n    if (sourceExcerpt != null) {\n      b.append(sourceExcerpt);\n      b.append('\\n');\n      int charno = error.getCharno();\n\n      // padding equal to the excerpt and arrow at the end\n      // charno == sourceExpert.length() means something is missing\n      // at the end of the line\nif(((excerpt.equals(LINE)"
                        postfix="for (int i = 0; i < charno; i++) {\n          char c = sourceExcerpt.charAt(i);\n          if (Character.isWhitespace(c)) {\n            b.append(c);\n          } else {\n            b.append(' ');\n          }\n        }\n        b.append(\"^\\n\");\n      }\n    }\n    return b.toString();\n  }"
                    elif id == "d4j_61a8cca68009e7c4a5d3d676":
                        prefix="@Override\n    public boolean isCachable() {\n        /* As per [databind#735], existence of value or key deserializer (only passed\n         * if annotated to use non-standard one) should also prevent caching.\n"
                        postfix="}"
                    elif id == "d4j_61a8cca68009e7c4a5d3d78e":
                        prefix="public boolean canInstantiate() {\nreturn"
                        postfix="}"
                    elif id =="d4j_61a8cca78009e7c4a5d3d9a4":
                        prefix="private boolean flipIfWarranted(final int n, final int step) {\n        if (1.5 * work[pingPong] < work[4 * (n - 1) + pingPong]) {\n"
                        postfix="for (int i = 0; i < j; i += 4) {\n                for (int k = 0; k < 4; k += step) {\n                    final double tmp = work[i + k];\n                    work[i + k] = work[j - k];\n                    work[j - k] = tmp;\n                }\n                j -= 4;\n            }\n            return true;\n        }\n        return false;\n    }"
                    elif id=="d4j_61a8cca68009e7c4a5d3d87f":
                        prefix="private void computeShiftIncrement(final int start, final int end, final int deflated) {\n\n        final double cnst1 = 0.563;\n        final double cnst2 = 1.010;\n        final double cnst3 = 1.05;\n\n        // a negative dMin forces the shift to take that absolute value\n        // tType records the type of shift.\n        if (dMin <= 0.0) {\n            tau = -dMin;\n            tType = -1;\n            return;\n        }\n\n        int nn = 4 * end + pingPong - 1;\n        switch (deflated) {\n\n        case 0 : // no realEigenvalues deflated.\n            if (dMin == dN || dMin == dN1) {\n\n                double b1 = Math.sqrt(work[nn - 3]) * Math.sqrt(work[nn - 5]);\n                double b2 = Math.sqrt(work[nn - 7]) * Math.sqrt(work[nn - 9]);\n                double a2 = work[nn - 7] + work[nn - 5];\n\n                if (dMin == dN && dMin1 == dN1) {\n                    // cases 2 and 3.\n                    final double gap2 = dMin2 - a2 - dMin2 * 0.25;\n                    final double gap1 = a2 - dN - ((gap2 > 0.0 && gap2 > b2) ? (b2 / gap2) * b2 : (b1 + b2));\n                    if (gap1 > 0.0 && gap1 > b1) {\n                        tau   = Math.max(dN - (b1 / gap1) * b1, 0.5 * dMin);\n                        tType = -2;\n                    } else {\n                        double s = 0.0;\n                        if (dN > b1) {\n                            s = dN - b1;\n                        }\n                        if (a2 > (b1 + b2)) {\n                            s = Math.min(s, a2 - (b1 + b2));\n                        }\n                        tau   = Math.max(s, 0.333 * dMin);\n                        tType = -3;\n                    }\n                } else {\n                    // case 4.\n                    tType = -4;\n                    double s = 0.25 * dMin;\n                    double gam;\n                    int np;\n                    if (dMin == dN) {\n                        gam = dN;\n                        a2 = 0.0;\n                        if (work[nn - 5]  >  work[nn - 7]) {\n                            return;\n                        }\n                        b2 = work[nn - 5] / work[nn - 7];\n                        np = nn - 9;\n                    } else {\n                        np = nn - 2 * pingPong;\n                        b2 = work[np - 2];\n                        gam = dN1;\n                        if (work[np - 4]  >  work[np - 2]) {\n                            return;\n                        }\n                        a2 = work[np - 4] / work[np - 2];\n                        if (work[nn - 9]  >  work[nn - 11]) {\n                            return;\n                        }\n                        b2 = work[nn - 9] / work[nn - 11];\n                        np = nn - 13;\n                    }\n\n                    // approximate contribution to norm squared from i < nn-1.\n                    a2 = a2 + b2;\n                    for (int i4 = np; i4 >= 4 * start + 2 + pingPong; i4 -= 4) {\n                        if(b2 == 0.0) {\n                            break;\n                        }\n                        b1 = b2;\n                        if (work[i4]  >  work[i4 - 2]) {\n                            return;\n                        }\n                        b2 = b2 * (work[i4] / work[i4 - 2]);\n                        a2 = a2 + b2;\n                        if (100 * Math.max(b2, b1) < a2 || cnst1 < a2) {\n                            break;\n                        }\n                    }\n                    a2 = cnst3 * a2;\n\n                    // rayleigh quotient residual bound.\n                    if (a2 < cnst1) {\n                        s = gam * (1 - Math.sqrt(a2)) / (1 + a2);\n                    }\n                    tau = s;\n\n                }\n            } else if (dMin == dN2) {\n\n                // case 5.\n                tType = -5;\n                double s = 0.25 * dMin;\n\n                // compute contribution to norm squared from i > nn-2.\n                final int np = nn - 2 * pingPong;\n                double b1 = work[np - 2];\n                double b2 = work[np - 6];\n                final double gam = dN2;\n                if (work[np - 8] > b2 || work[np - 4] > b1) {\n                    return;\n                }\n                double a2 = (work[np - 8] / b2) * (1 + work[np - 4] / b1);\n\n                // approximate contribution to norm squared from i < nn-2."
                        postfix="b2 = work[nn - 13] / work[nn - 15];\n                    a2 = a2 + b2;\n                    for (int i4 = nn - 17; i4 >= 4 * start + 2 + pingPong; i4 -= 4) {\n                        if (b2 == 0.0) {\n                            break;\n                        }\n                        b1 = b2;\n                        if (work[i4]  >  work[i4 - 2]) {\n                            return;\n                        }\n                        b2 = b2 * (work[i4] / work[i4 - 2]);\n                        a2 = a2 + b2;\n                        if (100 * Math.max(b2, b1) < a2 || cnst1 < a2)  {\n                            break;\n                        }\n                    }\n                    a2 = cnst3 * a2;\n                }\n\n                if (a2 < cnst1) {\n                    tau = gam * (1 - Math.sqrt(a2)) / (1 + a2);\n                } else {\n                    tau = s;\n                }\n\n            } else {\n\n                // case 6, no information to guide us.\n                if (tType == -6) {\n                    g += 0.333 * (1 - g);\n                } else if (tType == -18) {\n                    g = 0.25 * 0.333;\n                } else {\n                    g = 0.25;\n                }\n                tau   = g * dMin;\n                tType = -6;\n\n            }\n            break;\n\n        case 1 : // one eigenvalue just deflated. use dMin1, dN1 for dMin and dN.\n            if (dMin1 == dN1 && dMin2 == dN2) {\n\n                // cases 7 and 8.\n                tType = -7;\n                double s = 0.333 * dMin1;\n                if (work[nn - 5] > work[nn - 7]) {\n                    return;\n                }\n                double b1 = work[nn - 5] / work[nn - 7];\n                double b2 = b1;\n                if (b2 != 0.0) {\n                    for (int i4 = 4 * end - 10 + pingPong; i4 >= 4 * start + 2 + pingPong; i4 -= 4) {\n                        final double oldB1 = b1;\n                        if (work[i4] > work[i4 - 2]) {\n                            return;\n                        }\n                        b1 = b1 * (work[i4] / work[i4 - 2]);\n                        b2 = b2 + b1;\n                        if (100 * Math.max(b1, oldB1) < b2) {\n                            break;\n                        }\n                    }\n                }\n                b2 = Math.sqrt(cnst3 * b2);\n                final double a2 = dMin1 / (1 + b2 * b2);\n                final double gap2 = 0.5 * dMin2 - a2;\n                if (gap2 > 0.0 && gap2 > b2 * a2) {\n                    tau = Math.max(s, a2 * (1 - cnst2 * a2 * (b2 / gap2) * b2));\n                } else {\n                    tau = Math.max(s, a2 * (1 - cnst2 * b2));\n                    tType = -8;\n                }\n            } else {\n\n                // case 9.\n                tau = 0.25 * dMin1;\n                if (dMin1 == dN1) {\n                    tau = 0.5 * dMin1;\n                }\n                tType = -9;\n            }\n            break;\n\n        case 2 : // two realEigenvalues deflated. use dMin2, dN2 for dMin and dN.\n\n            // cases 10 and 11.\n            if (dMin2 == dN2 && 2 * work[nn - 5] < work[nn - 7]) {\n                tType = -10;\n                final double s = 0.333 * dMin2;\n                if (work[nn - 5] > work[nn - 7]) {\n                    return;\n                }\n                double b1 = work[nn - 5] / work[nn - 7];\n                double b2 = b1;\n                if (b2 != 0.0){\n                    for (int i4 = 4 * end - 9 + pingPong; i4 >= 4 * start + 2 + pingPong; i4 -= 4) {\n                        if (work[i4] > work[i4 - 2]) {\n                            return;\n                        }\n                        b1 *= work[i4] / work[i4 - 2];\n                        b2 += b1;\n                        if (100 * b1 < b2) {\n                            break;\n                        }\n                    }\n                }\n                b2 = Math.sqrt(cnst3 * b2);\n                final double a2 = dMin2 / (1 + b2 * b2);\n                final double gap2 = work[nn - 7] + work[nn - 9] -\n                Math.sqrt(work[nn - 11]) * Math.sqrt(work[nn - 9]) - a2;\n                if (gap2 > 0.0 && gap2 > b2 * a2) {\n                    tau = Math.max(s, a2 * (1 - cnst2 * a2 * (b2 / gap2) * b2));\n                } else {\n                    tau = Math.max(s, a2 * (1 - cnst2 * b2));\n                }\n            } else {\n                tau   = 0.25 * dMin2;\n                tType = -11;\n            }\n            break;\n\n        default : // case 12, more than two realEigenvalues deflated. no information.\n            tau   = 0.0;\n            tType = -12;\n        }\n\n    }"
                    elif id=="d4j_61a8cca68009e7c4a5d3d88d":
                        prefix="private String _handleOddName2(int startPtr, int hash, int[] codes) throws IOException\n    {\n        _textBuffer.resetWithShared(_inputBuffer, startPtr, (_inputPtr - startPtr));\n        char[] outBuf = _textBuffer.getCurrentSegment();\n        int outPtr = _textBuffer.getCurrentSegmentSize();\n        final int maxCode = codes.length;\n\n        while (true) {\n            if (_inputPtr >= _inputEnd) {\n                if (!_loadMore()) { // acceptable for now (will error out later)\n                    break;\n                }\n            }\n            char c = _inputBuffer[_inputPtr];\n            int i = (int) c;"
                        postfix=""
                try:
                    if sys in ["Tufano"]:
                        patch_line = patch_method.strip()
                    else:
                        assert prefix in patch_method
                        assert postfix in patch_method
                        patch_line = patch_method.replace(prefix, '', 1).replace(postfix, '').strip()
                    tool_names.append(sys)
                    bug_names.append(Bug_name)
                    buggy_lines.append(buggy_line)
                    develop_patch_lines.append(developer_line)
                    patch_indexes.append(candidate_indexes)
                    pred_lines.append(patch_line)
                    sub_ids.append(id)
                except:
                    print(id, candidate_indexes)

    df = pandas.DataFrame({"Bug-Name": bug_names, "Id": sub_ids, "NPR-System": tool_names, "Buggy-Line": buggy_lines,
                           "Develop-Patch-Line": develop_patch_lines,
                           "Patch-Index": patch_indexes, "Pred-Patch": pred_lines})
    df.to_excel(output_dir + '/d4j_' + sys + '.xlsx')
    pass
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/CoCoNut",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\CoCoNut\CoCoNut_300_d4j.patches",
                        #sys="CoCoNut",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/Edits",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Edits\Edits_d4j_b300.patches",
                        #sys="Edits",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/CodeBERT-ft",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\CodeBERT-ft\CodeBERT-ft_b300_d4j.patches",
                        #sys="CodeBERT-ft",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/SequenceR",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\SequenceR\SequenceR_b300_d4j.patches",
                        #sys="SequenceR",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/Tufano",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Tufano\Tufano_b300_d4j.patches",
                        #sys="Tufano",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/Recoder",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder\Recoder_d4j_b300.patches",
                        #sys="Recoder",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/Recoder_ori",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder_ori\recoder_ori_b300.patches",
                        #sys="Recoder_ori",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/RewardRepair_ori",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair_ori\d4j_ori.patches",
                        #sys="RewardRepair_ori",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/RewardRepair",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair\d4j_mine.patches",
                        #sys="RewardRepair",output_dir="D:/NPR4J-Eval-Results/manual_check")
#prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        #patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/RewardRepair_ori",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair_ori\d4j_ori.patches",
                        #sys="RewardRepair_ori",output_dir="D:/NPR4J-Eval-Results/manual_check")
prepare_d4j_for_check(d4j_info_f_1=r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",d4j_info_f_2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",
                        patch_dir="E:/NPR4J/ICSE23/NPR4J_Eval/d4j/Tufano",pred_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Tufano\Tufano_b300_d4j.patches",
                        sys="Tufano",output_dir="D:/NPR4J-Eval-Results/manual_check")