import pandas as pd

clone_data = pd.read_excel('C:/Users/SURFACE/OneDrive/Documents/Stage Lip6/ArgumentationProject/game_stats_simplified_1000_clones.xlsx')

average_clone_satisfaction = []
for data_row in clone_data.to_dict(orient='records'):
    clone_satisfactions = [] # a list keeping track of the satisfaction of all clones
    for i in range(max(1, int(data_row['Nb Clones']) )):
        final_value_clone = data_row['Agent ' + str(i) +' F.V.']
        final_value = data_row['F. V.']
        satisfaction = abs(final_value - final_value_clone)
        clone_satisfactions += [satisfaction]
        print(clone_satisfactions)
    average_satisfaction = sum(clone_satisfactions)/len(clone_satisfactions)
    average_clone_satisfaction += [average_satisfaction]

clone_data['Avg Clone Satisfaction'] = average_clone_satisfaction

clone_data.to_excel('game_stats_simplified_clones.xlsx')

    
