import networkx as nx
import plotly.graph_objects as go

def build_graph(skills,requirements,projects=None):
    G=nx.Graph()
    def node(kind,label):
        key=kind+':'+str(label);G.add_node(key,kind=kind,label=str(label));return key
    for r in skills.itertuples():
        e=node('Employee',r.Employee_ID);s=node('Skill',r.Skill);role=node('Role',r.Job_Role);d=node('Department',r.Department)
        G.add_edge(e,s,relation='HAS_SKILL',level=r.Skill_Level);G.add_edge(e,role,relation='WORKS_AS');G.add_edge(e,d,relation='BELONGS_TO')
    for r in requirements.itertuples():
        role=node('Role',r.Role);skill=node('Skill',r.Skill)
        G.add_edge(role,skill,relation='REQUIRES',level=r.Required_Level,capacity=int(r.Required_Employees))
    if projects is not None:
        for r in projects.itertuples():
            e=node('Employee',r.Employee_ID);p=node('Project',r.Project);s=node('Skill',r.Skill)
            G.add_edge(e,p,relation='ASSIGNED_TO');G.add_edge(p,s,relation='USES')
    return G

def plot_graph(G):
    if not G:raise ValueError('No graph nodes for these filters.')
    pos=nx.spring_layout(G,seed=42);x=[];y=[]
    for a,b in G.edges:x += [pos[a][0],pos[b][0],None];y += [pos[a][1],pos[b][1],None]
    fig=go.Figure(go.Scatter(x=x,y=y,mode='lines',line=dict(color='#CBD5E1',width=.7),hoverinfo='skip',showlegend=False))
    palette={'Employee':'#2563EB','Skill':'#0D9488','Role':'#7C3AED','Department':'#D97706','Project':'#DC5981'}
    for kind,color in palette.items():
        nodes=[n for n,v in G.nodes(data=True) if v['kind']==kind]
        if nodes:fig.add_trace(go.Scatter(x=[pos[n][0] for n in nodes],y=[pos[n][1] for n in nodes],text=[G.nodes[n]['label'] for n in nodes],mode='markers',marker=dict(color=color,size=10 if kind=='Employee' else 15),name=kind,hovertemplate='%{text}<extra>'+kind+'</extra>'))
    fig.update_layout(height=620,margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(visible=False),yaxis=dict(visible=False),plot_bgcolor='white')
    return fig
