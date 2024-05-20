import matplotlib.pyplot as plt

def draw_mrr_point():
    systems=["Recoder","SequenceR","CodeBERT-ft","Recoder_ori","RewardRepair","Tufano","CoCoNut","RewardRepair_ori","Edits"]
    x=[0.0751156410189965,0.047367053105668765,0.05968739695923818,0.060533601661984945,0.0676720876120195,
       0.015064001196493738,0.0358703946133863,0.06803744526137541,0.026771614473377163]
    y=[68,85,73,65,76,35,57,81,27]
    colors=['royalblue','royalblue','royalblue','grey','royalblue','royalblue','royalblue','grey','royalblue']
    markers=['o','1','^','o','s','p','d','s','>']
    plt.scatter(x[0], y[0],c=colors[0],marker=markers[0] )
    plt.scatter(x[1], y[1], c=colors[1], marker=markers[1],s=70)
    plt.scatter(x[2], y[2], c=colors[2], marker=markers[2])
    plt.scatter(x[3], y[3], c=colors[3], marker=markers[3])
    plt.scatter(x[4], y[4], c=colors[4], marker=markers[4])
    plt.scatter(x[5], y[5], c=colors[5], marker=markers[5])
    plt.scatter(x[6], y[6], c=colors[6], marker=markers[6])
    plt.scatter(x[7], y[7], c=colors[7], marker=markers[7])
    plt.scatter(x[8], y[8], c=colors[8], marker=markers[8])
    font = {'family': 'Times New Roman',
            'weight': 'normal',
            }
    plt.grid(b=True,
             color='grey',
             linestyle='--',
             linewidth=1,
             alpha=0.3,
             axis='x',
             which="major")
    plt.grid(b=True,
             color='grey',
             linestyle='--',
             linewidth=1,
             alpha=0.3,
             axis='y',
             which="major")
    plt.yticks(fontproperties='Times New Roman')
    plt.xticks(fontproperties='Times New Roman')
    plt.xlabel('Efficiency (MRR Score)',fontdict=font)
    plt.ylabel('Performance (Correct fixed bugs)',fontdict=font)
    plt.show()
draw_mrr_point()