import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../..')


import dash
import visdcc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from ArgumentationProject.graphs import DebateDAG,DebateGraph,DebateTree
from ArgumentationProject.run import run_debate

#### Utilities for Visualisation





def convert_to_visdcc_format(graph):
    """ Converts a networkx graph into a compatible format for visualisation with visdcc
    Returns : nodes a list of nodes
              edges a list of edges 
    """

    nodes = []
    for node in graph.nodes:
        color = '#8FC6F5'
        if node == 0:
            color = '#F5866A'
        nodes.append({'id': node, 'label': str(node), 'shape': 'circle', 'size': 14, 'color' :color})
    
    edges = []
    for edge in graph.edges:
        source, target = edge[0], edge[1]
        edges.append({
            'id': str(source) + "__" + str(target),
            'from': source,
            'to': target,
            'width': 2,
            'arrows':{'to':True}
        })
    
    return nodes, edges

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

# Create Data 
nb_of_arguments = 10

debate_model, game_stats = run_debate()

nodes, edges = convert_to_visdcc_format(debate_model.argument_graph)


# create app
app = dash.Dash()

value_string = "Original value : " + str(round(game_stats['Original Value'][0],4)) + "\n" + "Finale Value : " + str(round(debate_model.current_value, 4))
# define layout
app.layout = html.Div([
    html.H1(children='Debate Visualisation'),
    dcc.Checklist(id = 'display-table',
    options=[{'label': 'Show Stats'  , 'value': 'True'}, ],
    value=['False']) ,
    html.Div(id = 'output-table'),
    visdcc.Network(id = 'net', 
                     data = {'nodes': nodes, 'edges': edges},
                     options = dict(height= '600px', width= '100%'))
     
])

#+ str(game_stats['Original Value'][0] + "\n" + "Finale Value :" + str(debate_model.current_value))

# define callback
"""@app.callback(
    Output('net', 'options'),
    [Input('color', 'value')])
def myfun(x):
    return {'nodes':{'color': x}}"""

@app.callback(
    Output('output-table', 'children'),
    [Input('display-table', 'value')])
def display(input):
    print(input)
    if input[-1] == 'True':
        return generate_table(game_stats)
    else:
        return None

# define main calling
if __name__ == '__main__':
    app.run_server(debug=True)
