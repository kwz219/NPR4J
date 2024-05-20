from Analyze.AnalyzeBugTypes import count_all,count_composition,count_bugTypes,count_bugtypes_data_level,count_bugtypes_state
#find_fixed_longlogic, find_most_fixed_bugs, print_fixed_forflower, \
    #print_fixed_forupset, draw_bug_diffs, find_single_fixed_bugs, count_bugTypes, count_bugtypes_data_level, \
    #count_composition, count_bugtypes_state
from Analyze.Analyze_ContextLevel import draw_bugdiff_context, analyze_uncovered, analyze_hand
from Analyze.Analyze_MRR import calculate_MRR
from Analyze.Analyze_efficiency import prepare_data_4box, prepare_data_candidate_number
from Analyze.Analyze_plausible import Analyze_Plausible_top_k, prepare_plausible_data_4box,prepare_data_4line
from Analyze.Analyze_template import count_exclude_template
from Analyze.CountCorrect import count_system_fixed

#count_system_fixed(r"D:\文档\icse2023\d4j_result_2.json")
#count_system_fixed(r"D:\文档\icse2023\qbs_result.json")
#count_system_fixed(r"D:\文档\icse2023\bears_result.json")
#calculate_MRR(r"D:\文档\icse2023\d4j_result.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")
#count_all(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\d4j_result_2.json",
          #r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\bears_result.json",
          #r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\qbs_result.json")
#find_fixed_longlogic(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\d4j_result.json",
          #r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\bears_result.json",
          #r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\qbs_result.json")
#find_most_fixed_bugs(r"D:\文档\icse2023\d4j_result.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")
#Analyze_Plausible_top_k(r"D:\文档\icse2023\d4j_result_2.json",300)
#print_fixed_forflower(r"D:\文档\icse2023\d4j_result.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")
#count_exclude_template(r"D:\文档\icse2023\d4j_result_2.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")
#count_bugTypes(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\qbs_bugtypes.json",
               #r"D:\文档\icse2023\d4j_result_2.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")

#prepare_data_4box(r"D:\文档\icse2023\d4j_result_2.json",r"D:\文档\icse2023\qbs_result.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\box_plot.csv")
#count_bugtypes_data_level(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\d4j_result_2.json",
          #r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\bears_result.json",
          #r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\qbs_result.json",r"D:\文档\icse2023\level_count.csv")
#prepare_data_4line(r"D:\文档\icse2023\d4j_result.json",r"D:\文档\icse2023\qbs_result.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\He_line.csv")
#count_composition(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\d4j_result_2.json",
          #r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\bears_result.json",
          #r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\qbs_result.json")
#draw_bugdiff_context(r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\bears_bugtypes.json",
                    #"E:/NPR4J/RawData (2)/Benchmarks",r"D:\文档\icse2023\bugs_contextType.json")
#analyze_hand(r"D:\文档\icse2023\bugs_contextType.json","E:/NPR4J/RawData (2)/Benchmarks",r"D:\文档\icse2023\bugs_contextType2.json")
analyze_uncovered(r"D:\文档\icse2023\bugs_Types.json",r"D:\文档\icse2023\d4j_result_2.json",
                  r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json")
#count_bugtypes_state(r"D:\文档\icse2023\d4j_bugtypes.json",r"D:\文档\icse2023\d4j_result_2.json",
          #r"D:\文档\icse2023\bears_bugtypes.json",r"D:\文档\icse2023\bears_result.json",
          #r"D:\文档\icse2023\qbs_bugtypes.json",r"D:\文档\icse2023\qbs_result.json",r"D:\文档\icse2023\state_count.csv")
#prepare_data_candidate_number(r"D:\文档\icse2023\d4j_result_2.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json",
 #                             r"D:\文档\icse2023\repair_cn2.csv")
