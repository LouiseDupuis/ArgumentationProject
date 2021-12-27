"""import sys
#sys.path.insert(0,'..')
sys.path.insert(0,'../..')"""


from logging import raiseExceptions
from typing import Protocol
import dash
from matplotlib.pyplot import step
import visdcc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from graphs import DebateDAG,DebateGraph,DebateTree
from run import run_debate, run_debate_id
import pandas as pd
#### Utilities for Visualisation





def convert_to_visdcc_format(graph, semantic):
    """ Converts a networkx graph into a compatible format for visualisation with visdcc
    Returns : nodes a list of nodes
              edges a list of edges 
    """

    nodes = []
    for node in graph.nodes:
        color = '#8FC6F5'
        if node == 0:
            color = '#F5866A'
        title = "Test de titre"
        value = semantic.get_argument_value(node, graph)
        size = 20 * value + 5
        nodes.append({'id': node, 'label': str(node), 'shape': 'dot', 'size' : size, 'color' :color, 'title': title})
    
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

def generate_table(table, max_rows=10):

    dataframe = pd.DataFrame.from_records([table])
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



class GraphApp():

    """ Attributes : 
    - debate model 
    - game_stats 
    - app
    """

    def __init__(self) -> None:
        self.debate_model = None
        self.game_stats = None

        self.agent_graph = None





    def create_app(self):

        # create app
        self.app = dash.Dash(__name__)

        

        #define layout
        self.app.layout = html.Div([
            html.H1(children='Debate Visualisation'),

            html.Div( [
            
            html.Div([

            html.Div(["Number of Arguments: ",
                dcc.Input(id='input-nb-args', value='10', type='text')]),
            html.Div(["Number of Agents: ",
                dcc.Input(id='input-nb-agents', value='3', type='text')]),
            html.Div(["Number of Clones: ",
                dcc.Input(id='input-nb-clones', value='0', type='text')]),
            html.Div(["Comfort Limit: ",
                dcc.Input(id='input-cl', value='0.05', type='text')]),
            html.Div(["Proba of Learning - Favor: ",
                dcc.Input(id='input-p-favor', value='0.5', type='text')]),
            html.Div(["Proba of Learning - Against: ",
                dcc.Input(id='input-p-against', value='0.5', type='text')]),
            html.Div(["ID: ",
                dcc.Input(id='input-id', value='', type='text')]),

            dcc.Checklist( options=[
                {'label': 'Simplified Protocol', 'value': 'simplified'}],id='protocol-check', value=[]) ,
            
            html.Button('Run Simulation', id='run-button'),
            ], id = 'paramters'),
            html.Div([html.H2(children='Metrics'), 
            html.Div(id = 'output-table')], className='table-component')
            ], className='row'),


            

            #graph components : 
            html.Div([

            #======================= Original Graph ================================= 
            html.Div( [
                html.Div([html.H2(children='Complete Graph'), 
            html.Div(id='arg-graph'), html.Div(id = 'selected-nodes'),], className="block")], className='original-graph-component')
            ,

            # ====================== Final Graph ====================================
            html.Div([
                html.Div([html.H2(children='Final Graph'), 
            html.Div(id='final-graph'),], className='block'), 
            html.Div(id = 'f-selected-nodes'),
             html.Div( id = 'final-slider', children = dcc.Slider(
                                    id='slider',
                                    min = 0,
                                    value = 0,
                                    max = 0
                                )),
             html.H2(id='step-title'),
             html.Div(id='step-graph'),
             html.Div(id = 's-selected-nodes', children = '')
             ], className='column' ),

            # ===================== Agent Graphs ===========================================

            html.Div([html.H2(id = 'agent-title', children='Agent Graphs'),
                html.Div(id = 'agent-slider-container', children = dcc.Slider(
                                    id='agent-slider',
                                    min = 0,
                                    value  = 0,
                                    max = 0
                                )),
                dcc.Dropdown( id = 'agent-dropdown',
                        value=None
                    ),  
            html.Div(id='agent-graph')
            , html.Div(id = 'a-selected-nodes'), html.Div(id = 'agent-info')], className='column' )
        
            
            ],  className='row')
            
        ])
        
        ##============= MAIN CALLBACK========================================
        @self.app.callback(
            [Output('arg-graph', 'children'), Output('final-graph', 'children'), Output('output-table', 'children'), Output('agent-dropdown', 'options'), Output('slider', 'max'), Output('agent-slider', 'max')],
            [Input('input-nb-args', 'value'),Input('input-nb-agents', 'value'), Input('input-nb-clones', 'value'), Input('input-cl', 'value'),Input('input-p-favor', 'value'), Input('input-p-against', 'value') ,Input('run-button', 'n_clicks')], Input('input-id', 'value')
            ,Input('protocol-check', 'value') )
        def run_simulation(nb_agents, nb_args, nb_clones, comfort_limit, p_favor_bias, p_against_bias, nb_clicks, id, protocol):

            if nb_clicks is not None:
                changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
                if 'run-button' in changed_id:
                    
                    if len(protocol) != 0:
                        protocol = protocol[0]
                    else:
                        protocol = 'complete'
                    print(protocol)

                    if id is not None and len(id)>0:
                        print(id)
                        self.debate_model, self.game_stats = run_debate_id(id, protocol=protocol)
                    
                    else:
                        try:
                            nb_args = int(nb_args)
                            nb_agents = int(nb_agents)
                            nb_clones = int(nb_clones)
                            comfort_limit = float(comfort_limit)
                            p_favor_bias = float(p_favor_bias)
                            p_against_bias = float(p_against_bias)
                        except:
                            raise("Invalid Arguments")
                        
                        self.debate_model, self.game_stats = run_debate(nb_args, nb_agents, lightmode=False, comfort_limit=comfort_limit, 
                                                                            p_favor_bias=p_favor_bias, p_against_bias=p_against_bias, protocol=protocol, number_of_clones=nb_clones)
                    nodes, edges = convert_to_visdcc_format(self.debate_model.argument_graph, self.debate_model.semantic)

                    final_nodes, final_edges = convert_to_visdcc_format(self.debate_model.public_graph, self.debate_model.semantic)

                    # building the options for the agent dropdown 

                    dropdown_options=[
                            {'label': 'Merged Graph', 'value': 'Merged'}
                        ]
                    for agent in self.debate_model.schedule.agents:
                        dropdown_options += [{'label': 'Agent ' + str(agent.name), 'value': agent.name}]

                    return [visdcc.Network(id = 'net', selection = {'nodes':[], 'edges':[]},data ={'nodes': nodes, 'edges': edges}, options = dict(height= '400px', width= '100%', interaction = dict(hover= True))), 
                            visdcc.Network(id = 'f-graph', selection = {'nodes':[], 'edges':[]},data ={'nodes': final_nodes, 'edges': final_edges}, options = dict(height= '350px', width= '100%', interaction = dict(hover= True))), 
                            generate_table(self.game_stats), 
                            dropdown_options,
                            self.game_stats['Steps'] - 1,
                            self.game_stats['Steps'] - 1]
                               
            
            return (None, None, None, [], 0, 0)

        @self.app.callback(
            [Output('agent-graph', 'children'),Output('agent-title', 'children'), Output('agent-info', 'children')],
            [Input('agent-dropdown', 'value'), Input('agent-slider', 'value'), Input('arg-graph', 'children')])
        def update_output(value, step, arg_graph):
            if self.debate_model is not None and value is not None :
                if value =='Merged':
                    merged_value, merged_graph = self.debate_model.get_merged_value(step)
                    print("MERGED VALUE : ", merged_value)
                    nodes, edges = convert_to_visdcc_format(merged_graph, self.debate_model.semantic)
                    title = "Merged Graph Step " + str(step)
                    self.agent_graph = merged_graph
                    return [visdcc.Network(id = 'agent-net',selection = {'nodes':[], 'edges':[]}, data ={'nodes': nodes, 'edges': edges},
                                options = dict(height= '400px', width= '100%', interaction = dict(hover= True))), title, None]
                else:
                    for agent in self.debate_model.schedule.agents:
                        if agent.name == value:
                            g = agent.state[step]
                            self.agent_graph = g
                            g.view_graph()
                            nodes, edges = convert_to_visdcc_format(agent.state[step], self.debate_model.semantic)
                            title = "Agent Graphs Step " + str(step)


                            strategy = "Strategy : " + str(self.debate_model.strategies[step][agent.name][0])

                            return [visdcc.Network(id = 'agent-net',selection = {'nodes':[], 'edges':[]}, data ={'nodes': nodes, 'edges': edges},
                                        options = dict(height= '400px', width= '100%', interaction = dict(hover= True))), 
                                    title, html.Div([html.H4('Agent Information'), strategy]) ]
                

            return None, 'Agent Graphs', None
        

        @self.app.callback(
        [dash.dependencies.Output('step-graph', 'children'),dash.dependencies.Output('step-title', 'children')],
        [dash.dependencies.Input('slider', 'value'), Input('final-graph', 'children') ])
        def update_step_graph(value, final_graph):
            if value is not None and self.debate_model is not None:
                graph = self.debate_model.state[value]
                nodes, edges = convert_to_visdcc_format(graph, self.debate_model.semantic)
                return [visdcc.Network(id = 'step-net',selection = {'nodes':[], 'edges':[]}, data ={'nodes': nodes, 'edges': edges},
                            options = dict(height= '400px', width= '100%', interaction = dict(hover= True))),
                            "Public Graph Step " + str(value)]
            return None, None
        

        # Callback for selection in original graph :
        @self.app.callback(
        Output('selected-nodes', 'children'),
        [Input('net', 'selection')])
        def myfun(x): 
            s = ''
            if len(x['nodes']) > 0 :
                argument = x['nodes'][0]
                s += "Argument "+str(argument)
                weight = self.debate_model.argument_graph.get_argument_weight(argument)
                value = self.debate_model.semantic.get_argument_value(argument, self.debate_model.argument_graph)
                s += "\n Weight : " + str(weight) + " \n Value : " + str(value)
            return dcc.Markdown(s, style={"white-space": "pre"})
        
        # Callback for selection in final graph
        @self.app.callback(
        Output('f-selected-nodes', 'children'),
        [Input('f-graph', 'selection')])
        def myfun(x): 
            s = ''
            if len(x['nodes']) > 0 :
                argument = x['nodes'][0]
                s += "Argument " + str(argument)
                upvotes, downvotes = self.debate_model.public_graph.get_argument_votes(argument)
                up_list = self.debate_model.public_graph.nodes[argument]["up_list"]
                down_list = self.debate_model.public_graph.nodes[argument]["down_list"]
                weight = self.debate_model.public_graph.get_argument_weight(argument)
                value = self.debate_model.semantic.get_argument_value(argument, self.debate_model.public_graph)
                s += "\n " + str(upvotes) + " +  [" + str(up_list) + "] | " + str(downvotes) + " - " + str(down_list) + "\n Weight : " + str(weight) + " \n Value : " + str(value)
            return dcc.Markdown(s, style={"white-space": "pre"})

        # Callback for selection in step graph
        @self.app.callback(
        Output('s-selected-nodes', 'children'),
        [Input('step-net', 'selection'), dash.dependencies.Input('slider', 'value')])
        def myfun(x, value): 
            s = ''
            if x is not None and len(x['nodes']) > 0 :

                graph = self.debate_model.state[value]
                argument = x['nodes'][0]
                s += "Argument " + str(argument)
                upvotes, downvotes = graph.get_argument_votes(argument)
                weight = graph.get_argument_weight(argument)
                up_list = graph.nodes[argument]["up_list"]
                down_list = graph.nodes[argument]["down_list"]
                value = self.debate_model.semantic.get_argument_value(argument, graph)
                s += "\n " + str(upvotes) + " +  [" + str(up_list) + "] | " + str(downvotes) + " - [" + str(down_list)  + " ] \n Weight : " + str(weight) + " \n Value : " + str(value)
                return dcc.Markdown(s, style={"white-space": "pre"})
            return None
        

        # Callback for selection in agent graph
        @self.app.callback(
        Output('a-selected-nodes', 'children'),
        [Input('agent-net', 'selection'), Input('agent-slider', 'value'), Input('agent-dropdown', 'value')])
        def myfun(x, step, agent): 
            s = ''
            if x is not None and len(x['nodes']) > 0 :

                graph = self.agent_graph
                argument = x['nodes'][0]
                s += "Argument " + str(argument)
                weight = graph.get_argument_weight(argument)
                value = self.debate_model.semantic.get_argument_value(argument, graph)

                if agent == "Merged":
                    upvotes, downvotes = graph.get_argument_votes(argument)
                    up_list = graph.nodes[argument]["up_list"]
                    down_list = graph.nodes[argument]["down_list"]
                    s += "\n " + str(upvotes) + " +  [" + str(up_list) + "] | " + str(downvotes) + " - [ " + str(down_list)  +" ] \n Weight : " + str(weight) + " \n Value : " + str(value)
                    return dcc.Markdown(s, style={"white-space": "pre"})

                s += "\n Weight : " + str(weight) + " \n Value : " + str(value)
                return dcc.Markdown(s, style={"white-space": "pre"})
            return None


                        


            
        
        return self.app

# define main calling
if __name__ == '__main__':

    graph_app = GraphApp()
    graph_app.create_app()

    graph_app.app.run_server(debug=True)







### dcc.Checklist(id = 'display-table',
###        options=[{'label': 'Show Stats'  , 'value': 'True'}, ],
###        value=['False']) ,