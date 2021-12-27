import xgboost
import shap
import pandas as pd
from sklearn import linear_model
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
# train an XGBoost model
#X, y = shap.datasets.boston()


data = pd.read_excel('C:/Users/SURFACE/OneDrive/Documents/Stage Lip6/ArgumentationProject/game_stats_simplified_agent_power.xlsx')
# building y = agent dissatisfaction 
# building X = feature of agent's power
y = []
y_rank = []
X_list = []
agent_index = 0

for data_row in data.to_dict(orient='records'):
    final_value = data_row['F. V.']

    debate_merged_influence_index = []

    debate_x = []

    debate_statisfaction = []

    for i in range(7):
        #building y
        final_value_agent = data_row['Agent ' + str(i) +' F.V.']
        y_agent = abs(final_value - final_value_agent)
        y += [y_agent]
        debate_statisfaction += [y_agent]

        #building x
        number_of_arguments = data_row['Agent ' + str(i) +' O. N. Args']
        opinion_influence_index = data_row['Agent ' + str(i) +' Opinion Influence Index']
        merged_influence_index = data_row['Agent ' + str(i) +' Merged Influence Index']
        debate_merged_influence_index += [merged_influence_index]

        consensus_index = 0
        relative_knowledge_index = 0
        for j in range(7):
            consensus_index += data_row['Agent ' + str(i) + ' Agent '+ str(j) + " Common Arguments" ]
            relative_knowledge_index += data_row['Agent ' + str(i) + ' O. N. Args'] - data_row['Agent ' + str(j) + ' O. N. Args']
        #original_agent_value = data_row['Agent ' + str(i) +' O.V.']
        x_agent = [agent_index, number_of_arguments, opinion_influence_index, merged_influence_index, consensus_index, relative_knowledge_index]
        debate_x += [x_agent]
    #adding the ranks
    #
    sorted_list = sorted(debate_merged_influence_index) 
    sorted_sat = sorted(debate_statisfaction)
    for i in range(7):
        index_rank = sorted_list.index(debate_merged_influence_index[i])
        satisfaction_rank = sorted_sat.index(debate_statisfaction)
        debate_x[i] += [index_rank]
        y_rank += [satisfaction_rank]
    X_list += [debate_x]



X = pd.DataFrame(X_list, columns=['index', 'Number of Arguments', 'Influence Index (Opinion)', 'Influence Index (Merged)', 'Consensus Index', 'Relative Knowledge Index', 'Merged Influence Rank'])
"""model = xgboost.XGBRegressor().fit(X, y)

# explain the model's predictions using SHAP
# (same syntax works for LightGBM, CatBoost, scikit-learn, transformers, Spark, etc.)
explainer = shap.Explainer(model)
shap_values = explainer(X)

# visualize the first prediction's explanation
shap.plots.waterfall(shap_values[0])"""

# Predicting satisfaction
for feature in X.columns:
    reg = linear_model.LinearRegression(normalize = True)

    slope, intercept, r_value, p_value, std_err = stats.linregress(X[feature],y)
    print(feature, slope, r_value**2, p_value)

    plt.plot(X[feature], y, 'o')
    plt.plot(X[feature], intercept + slope*X[feature], 'r', label= 'y = ' + str(round(slope,4)) + "*X + " + str(round(intercept,4)))
    plt.legend()
    plt.show()

# Predicting rank
for feature in X.columns:
    reg = linear_model.LinearRegression(normalize = True)

    slope, intercept, r_value, p_value, std_err = stats.linregress(X[feature],y_rank)
    print(feature, slope, r_value**2, p_value)

    plt.plot(X[feature], y, 'o')
    plt.plot(X[feature], intercept + slope*X[feature], 'r', label= 'y = ' + str(round(slope,4)) + "*X + " + str(round(intercept,4)))
    plt.legend()
    plt.show()


    