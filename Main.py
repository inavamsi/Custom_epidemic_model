import ReadFile
import World
import streamlit as st
import Model
import networkx as nx
import matplotlib.pyplot as plt1

st.write("""
# Agent based custom compartment model
Customised epidemic compartment model on a complete graph using Episimmer codebase
""")
st.write("For any queries please email ibe214@nyu.edu")
st.write("------------------------------------------------------------------------------------")

interactions_files_list=None
events_files_list=None
locations_filename=None
config_obj=ReadFile.ReadConfiguration()



def generate_policy():
	policy_list=[]

	def event_restriction_fn(agent,event_info,current_time_step):
		return False

	return policy_list,event_restriction_fn

def write_agents(filename,n):
	header='Agent Index'

	f=open(filename,'w')
	f.write(str(n)+'\n')
	f.write(header+'\n')

	for i in range(n):
		f.write(str(i)+'\n')

def write_events(filename,no_locations,no_agents):
	info_dict={}
	#ID enumerates from 0 to n-1
	header='Location Index:Agents'

	f=open(filename,'w')
	f.write(str(1)+'\n')
	f.write(header+'\n')

	line=str(0)+':'
	for i in range(no_agents):
		line+=str(i)
		if i!=no_agents-1:
			line+=','

	f.write(line)

policy_list, event_restriction_fn=generate_policy()

filename='one_event.txt'
no_locations=1
no_agents=st.sidebar.slider("Select number of agents", min_value=0 , max_value=1000 , value=300 , step=10 , format=None , key=None )
write_agents('agents.txt',no_agents)
write_events('one_event.txt',1,no_agents)
days=st.sidebar.slider("Select number of days", min_value=1 , max_value=200 , value=100 , step=1 , format=None , key=None )
worlds=st.sidebar.slider("Select number of worlds", min_value=1 , max_value=30 , value=5 , step=1 , format=None , key=None )
config_obj.worlds=worlds
config_obj.time_steps=days

no_states=st.sidebar.slider("Select number of compartments", min_value=1 , max_value=10 , value=3 , step=1 , format=None , key=None )
no_transitions=st.sidebar.slider("Select number of transitions", min_value=0 , max_value=30 , value=2 , step=1 , format=None , key=None )

individual_types=[]
infected_states=[]
state_proportion={}

for i in range(no_states):
	st.header("Compartment "+str(i+1))
	col1, col2 = st.beta_columns(2)
	default='None'
	if i==0:
		default='Susceptible'
	if i==1:
		default='Infected'
	if i==2:
		default='Recovered'

	state = col1.text_input("Name of compartment "+str(i+1), default)
	infectious=False
	initial_prop=0
	inf_default=False
	if i==1:
		inf_default=True
	if state !='None':
		infectious = st.checkbox("Is compartment \'"+state+"\' infectious?",inf_default)
	if i==0 and no_states>1:
		val=0.99
	elif i==0 and no_states==1:
		val=1.0
	elif i==1:
		val=0.01
	else:
		val=0.0
	if state!='None':
		initial_prop = col2.slider("Intial proportion of \'"+state+"\'", min_value=0.0 , max_value=1.0 , value=val , step=0.01 , format=None , key=None )

	if state!='None':
		individual_types.append(state)
		if infectious:
			infected_states.append(state)
		state_proportion[state]=initial_prop

st.write("------------------------------------------------------------------------------------")


G = nx.DiGraph()

infectious_dict={}
model = Model.StochasticModel(individual_types,infected_states,state_proportion)
for i in range(no_transitions):
	st.header("Transition "+str(i+1))
	def_bool=False
	if i==0 and infected_states!=[]:
		def_bool=True
	p_infection = st.checkbox("Does transition "+str(i+1)+" depend on infectious states?",def_bool)
	col1, col2, col3 = st.beta_columns(3)
	def_s1=def_s2=0
	if i==0 and no_states>1:
		def_s1=0
		def_s2=1
	if i==1 and no_states>2:
		def_s1=1
		def_s2=2
	state1 = col1.selectbox("Initial compartment for transition "+str(i+1),individual_types,index=def_s1)
	state2 = col2.selectbox("Final compartment for transition "+str(i+1),individual_types,index=def_s2)
	G.add_edge(state1, state2)
	if p_infection:
		l=[]
		for istate in infected_states:
			l.append(None)
			infectious_dict[istate]=float(col3.text_input("Rate of infection from compartment "+istate+ " for transition "+str(i+1), 0.01))
		model.set_transition(state1, state2, model.p_infection(l,None))
	else:
		rate=float(col3.text_input("Rate constant for transition "+str(i+1), 0.03))
		model.set_transition(state1, state2, model.p_standard(rate))


def event_contribute_fn(agent,event_info,location,current_time_step):
		if agent.state in infected_states:
			return infectious_dict[agent.state]
		return 0

def event_recieve_fn(agent,ambient_infection,event_info,location,current_time_step):
	#Example 1
	beta=0.1
	return ambient_infection*beta

model.set_event_contribution_fn(event_contribute_fn)
model.set_event_recieve_fn(event_recieve_fn)


#plt1.title('Custom compartment model')
#nx.draw_networkx(G, with_label = False, node_color ='green')
#st.pyplot(plt1)


agents_filename=config_obj.agents_filename
interactions_FilesList_filename=config_obj.interactions_files_list
if config_obj.locations_filename=="":
	locations_filename=None
else:
	locations_filename=config_obj.locations_filename
events_FilesList_filename=config_obj.events_files_list

if config_obj.interactions_files_list=='':
	print('No Interaction files uploaded!')
else:
	interactionFiles_obj=ReadFile.ReadFilesList(interactions_FilesList_filename)
	interactions_files_list=list(map(lambda x : x ,interactionFiles_obj.file_list))
	if interactions_files_list==[]:
		print('No Interactions inputted')

if config_obj.events_files_list=='':
	print('No Event files uploaded!')
else:
	eventFiles_obj=ReadFile.ReadFilesList(events_FilesList_filename)
	events_files_list=list(map(lambda x : x ,eventFiles_obj.file_list))
	if events_files_list==[]:
		print('No Events inputted')


world_obj=World.World(config_obj,model,policy_list,event_restriction_fn,agents_filename,interactions_files_list,locations_filename,events_files_list)
world_obj.simulate_worlds()
