import inspect
import matplotlib.pyplot as plt
import sys
print (sys.version)
from matplotlib import rcParams
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib.ticker as ticker
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessHour
from tqdm import tqdm
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import datetime
import inspect #for code_begin() and code_end()
import matplotlib.font_manager# config.py

'''
Sets up global flag that determine which functions run.
Also sets up settings (rcparams) for Charting
'''


show_visualizatons = False

DELETE_EXISTNG_OUTPUT_FILES = False
DISPLAY_VISUALIZATIONS = True
SAVE_VISUALIZATIONS = True
SAVE_DATA = True

##################
# master over-rides individual Booleans
#master_flag = True
# Individual Booleans
create_electr_frcst_dicts_flag = True 
check_integrity_of_input_data_flag = True
process_forecast_data_flag = True
stats_on_frcst_data_flag = True
generate_p_values_flag = True
calc_lcoe_flag = False 
simulate_merit_order_flag = False
adjust_frcst_data_flag = False
enb_load_review_flag = False
create_trans_costs_flag = False

print(f"create_electr_frcst_dicts_flag: {create_electr_frcst_dicts_flag} ")
print(f"check_integrity_of_input_data_flag: {check_integrity_of_input_data_flag} ")
print(f"process_forecast_data_flag: {process_forecast_data_flag} ")
print(f"stats_on_frcst_data_flag: {stats_on_frcst_data_flag} ")
print(f"generate_p_values_flag: {generate_p_values_flag} ")
print(f"calc_lcoe_flag: {calc_lcoe_flag} ")
print(f"simulate_merit_order_flag: {simulate_merit_order_flag} ")
print(f"adjust_frcst_data_flag: {adjust_frcst_data_flag} ")
print(f"enb_load_review_flag: {enb_load_review_flag} ")
print(f"create_trans_costs_flag: {create_trans_costs_flag}")

#Print Results

# List of all boolean variables
boolean_flags = [
    create_electr_frcst_dicts_flag,
    check_integrity_of_input_data_flag,
    process_forecast_data_flag,
    stats_on_frcst_data_flag,
    generate_p_values_flag,
    calc_lcoe_flag,
    simulate_merit_order_flag,
    adjust_frcst_data_flag,
    enb_load_review_flag,
    create_trans_costs_flag
]

# Check if all booleans are True
runpipe_all_flags_true = all(boolean_flags)
print(runpipe_all_flags_true)  # This will print False since not all flags are True

############################################
# Globally defined functions and Variables
############################################
def set_custom_rcparams():
    print("set_custom_rcparams called")
    # -- Axes --
    rcParams['axes.spines.bottom'] = True
    rcParams['axes.spines.left'] = False
    rcParams['axes.spines.right'] = False
    rcParams['axes.spines.top'] = False

    rcParams['axes.axisbelow'] = True
    rcParams['axes.linewidth'] = 2
    rcParams['axes.ymargin'] = 0

    # -- Grid

    # Enable both major and minor grid lines globally
    rcParams['axes.grid'] = True
    rcParams['axes.grid.axis'] = 'y'
    rcParams['grid.color'] = 'grey'
    rcParams['grid.linewidth'] = 0.5
    rcParams['grid.linestyle'] = '--'

    plt.rcParams['axes.grid.which'] = 'both'   # Apply grid lines to both major and minor ticks
    plt.rcParams['grid.alpha'] = 0.5           # Transparency of grid lines

    # Enable minor ticks globally
    plt.rcParams['xtick.minor.visible'] = True # Show x-axis minor ticks
    plt.rcParams['ytick.minor.visible'] = True # Show y-axis minor ticks

    # Configure minor tick parameters
    # plt.rcParams['xtick.minor.bottom'] = False # Disable minor ticks at the bottom
    # plt.rcParams['ytick.minor.left'] = False   # Disable minor ticks on the left

    # You can also set other properties like color, width, size if needed
    # For example, setting the color and width of the grid lines
    plt.rcParams['grid.color'] = 'grey'        # Color of grid lines

    # -- Ticks and tick labels --
    rcParams['axes.edgecolor'] = 'grey'
    rcParams['xtick.color'] = 'grey'
    rcParams['ytick.color'] = 'grey'
    rcParams['xtick.major.width'] = 2
    rcParams['ytick.major.width'] = 0
    rcParams['xtick.major.size'] = 5
    rcParams['ytick.major.size'] = 0

    # -- Fonts --
    rcParams['font.size'] = 16
    #rcParams['font.family'] = 'LiberationMono-Regular' #'serif'
    rcParams.update({"font.family": "Calibri", "font.weight": "light"})
    rcParams['text.color'] = 'grey'
    rcParams['axes.labelcolor'] = 'grey'

    # -- Figure size --
    rcParams['figure.dpi'] = 100
    rcParams['figure.figsize'] = (8, 4)
    
    rcParams['legend.facecolor'] ='white'
    rcParams['legend.framealpha']  = 1
    #........................................
    #OTHER
    #........................................
    # -- Saving Options --
    rcParams['savefig.bbox'] = 'tight'
    rcParams['savefig.dpi'] = 500
    rcParams['savefig.transparent'] = True

    # navy = (56 / 256, 74 / 256, 143 / 256)
    # teal = (106 / 256, 197 / 256, 179 / 256)
    # pink = [199 / 255, 99 / 255, 150 / 255]

    # rcParams['axes.prop_cycle'] = cycler(color=[teal, navy, pink])
    return rcParams

#These create start/end message for each routine to support debugging
def code_begin():
    # Getting the name of the caller function
    caller_name = inspect.stack()[1][3]
    print(f"{caller_name} Started")
    

def code_end():
    # Getting the name of the caller function
    caller_name = inspect.stack()[1][3]
    print(f"{caller_name} Completed")
    print("*" * 90)


#ide_option = "vscode" #'vscode', 'jupyter_notebook', 'kaggle' 


############################################
#Graphing Configuration
############################################

#-------------------------------------------
#Matplolib Chart Configuration
#-------------------------------------------
#Set rcParams

code_begin()


    
def reset_rcparams_to_default():
    mpl.rcdefaults()
    
    
#-------------------------------------------
#Plotly Chart Configuration
#-------------------------------------------

# Plotly, unlike Matplotlib, does not use a global configuration system like rcParams. 
# Instead, styling and configuration in Plotly are done on a per-chart basis using the 
# chart's layout and style attributes. However, you can create a function to apply a 
# consistent style to your Plotly charts, similar to setting custom rcParams in Matplotlib. 
# This function would modify the layout and style properties of a given Plotly figure. 
    


def apply_custom_style_to_plotly(fig):
    # Axes styles
    fig.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='grey', color='grey', linewidth=2, tickwidth=2, ticklen=5)
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='grey', color='grey', linewidth=0, tickwidth=0, ticklen=0)

    # Figure styles
    fig.update_layout(
        font=dict(size=16, family="Calibri", color='grey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(bgcolor='white', font=dict(color='grey')),
        margin=dict(t=60, l=0, r=0, b=0)  # Adjusted top margin so you can see the chart title
    )

    # Additional styles can be added as needed
    return fig
    
code_end()

#-------------------------------------------
# Set rcParams
#-------------------------------------------
set_custom_rcparams()

#-------------------------------------------
# Set-up Color Palletes, Fonts, and Graphs Settings
#-------------------------------------------
# #Set-up Fonts
# font1 = {'family':'fantasy','color':'blue','size':20}
# font2 = {'family':'serif','color':'darkred','size':15}
# font3 = {'family':'cursive','color':'green','size':20}

code_begin()

#-------------------------------------------
#matplotlib/seaborn
#-------------------------------------------
#Set-up Graph Background:
# Use a dark theme
#plt.style.use('dark_background')

# Reset the background style to the default one
plt.rcdefaults()

# Enable grid lines, horizontal only, with a darker gray color
plt.grid(axis='y', color='gray', linestyle='-', linewidth=0.5)


# Configuration cell
# Not we have a category called Unknown which gets teh DEFAULT Value

# Set global legend style
plt.rcParams['legend.facecolor'] = 'white'
plt.rcParams['legend.edgecolor'] = 'black'

#-------------------------------------------
#TECH_TYPE Config
#-------------------------------------------
# Define the desired order of the technology types
tech_type_desired_order = [
    'COAL','COGENERATION','COMBINED_CYCLE','HYDRO','DUAL_FUEL','SIMPLE_CYCLE','GAS_FIRED_STEAM', 'OTHER','SOLAR', 'WIND', 'UNKNOWN','ENERGY_STORAGE', 'TIE_LINE'
]

tech_type_list_plus_BTF = [
    'COAL','COGENERATION','COMBINED_CYCLE','HYDRO','DUAL_FUEL','SIMPLE_CYCLE','GAS_FIRED_STEAM', 'OTHER','SOLAR', 'WIND', 'UNKNOWN','ENERGY_STORAGE', 'TIE_LINE', 'BTF_GENERATION'
]


original_tech_type_desired_order = tech_type_desired_order.copy()

#-------------------------------------------
#Color Palette Config
#-------------------------------------------

# Define your custom color palette
custom_color_palette = {
    'Grey': '#555555',
    'Gold': '#FFB81C',
    'White': '#FFFFFF',
    'Clementine': '#FF6900',
    'Cherry': '#C8102E',
    'Plum': '#720062',
    'Mint': '#3CDBC0',
    'Leaf': '#6CC24A',
    'Moss': '#4A773C',
    'Sky': '#59CBE8',
    'Ocean': '#007DBA',
    'Dusk': '#280071',
    'Steel': '#D0D0CE',
    'Slate': '#97999B',
    'Black': '#000000',
    'Yellow' :'#f9f93d' #new for solar
}

# Map your technology types to the custom colors
tech_type_colors = {
    'COAL': custom_color_palette['Black'],
    'COGENERATION': custom_color_palette['Mint'],  # example, assuming you want to map it to 'Leaf'
    'COMBINED_CYCLE': custom_color_palette['Grey'],
    'HYDRO' : custom_color_palette['Sky'],
    'DUAL_FUEL': custom_color_palette['Steel'],
    'SIMPLE_CYCLE' : custom_color_palette['Slate'],
    'GAS_FIRED_STEAM': custom_color_palette['Plum'],
    'OTHER': custom_color_palette['Clementine'],
    'SOLAR': custom_color_palette['Yellow'], #was 'Cherry'
    'WIND': custom_color_palette['Leaf'],
    'UNKNOWN': custom_color_palette['Moss'],
    'ENERGY_STORAGE': custom_color_palette['Ocean'],
    'TIE_LINE': custom_color_palette['Dusk'],
    'BTF_GENERATION' :  custom_color_palette['White']
}


original_color_map = tech_type_colors.copy()



# Create a font color map
tech_type_font_colors = {
    'COAL': 'white',
    'COGENERATION': 'white',
    'COMBINED_CYCLE': 'white',
    'HYDRO': 'black',
    'DUAL_FUEL': 'black',
    'SIMPLE_CYCLE': 'black',
    'GAS_FIRED_STEAM': 'white',
    'OTHER': 'black',
    'SOLAR': 'black', #was white
    'WIND': 'black',
    'UNKNOWN': 'white',
    'ENERGY_STORAGE': 'white',
    'TIE_LINE': 'white',
    'BTF_GENERATION' : 'white'
}



# Make a copy of the color map so that you can revert back to its original state
# in the event that it is changed later in the routine.Remember that althoght
# these dictionaries are public objects, Python allows them to be "mutable" and 
# they can change in any module or cell in a Pythpon projects

#Example:
# Change the color map for specific plots
# tech_type_colors = dict(zip(unique_tech_types, colors))
# Plot your graphs here
# Revert to the original color map
# tech_type_colors = original_color_map 


# Define custom line thickness for each TECH_TYPE
tech_type_custom_line_thickness = {
    'COAL': 3.0,
    'COGENERATION': 3.0,
    'COMBINED_CYCLE': 3.0,
    'HYDRO': 3.0,
    'DUAL_FUEL': 3.0,
    'SIMPLE_CYCLE': 3.0,
    'GAS_FIRED_STEAM': 3.0,
    'OTHER': 3.0,
    'SOLAR': 5.0,
    'WIND': 5.0,
    'UNKNOWN': 3.0,
    'ENERGY_STORAGE': 5.0,
    'TIE_LINE' : 3.0,
    'BTF_GENERATION' : 1.0
}   
    
tech_type_markers = {
    'COAL': '>',
    'COGENERATION': 'D',
    'COMBINED_CYCLE': 's',
    'HYDRO': '<',
    'DUAL_FUEL': '^',
    'SIMPLE_CYCLE': 'v',
    'GAS_FIRED_STEAM': 'p',
    'OTHER': 'x',
    'SOLAR': 'o',
    'WIND': 'h',
    'UNKNOWN': '^',
    'ENERGY_STORAGE': '8',
    'TIE_LINE' : '*', 
    'BTF_GENERATION' : 'o'
}

#(0, (1, 10))
tech_type_custom_line_styles = {
    'COAL': '-',
    'COGENERATION': '--',
    'COMBINED_CYCLE': '-.',
    'HYDRO': ':',
    'DUAL_FUEL': (0, (3, 5, 1, 5)),  # Example of a custom dash pattern
    'SIMPLE_CYCLE': '-',
    'GAS_FIRED_STEAM': (0, (5, 10)),
    'OTHER': (0, (3, 1, 1, 1)),
    'SOLAR': (0, (3, 5, 1, 5, 1, 5)),
    'WIND': (0, (5, 1)),
    'UNKNOWN': '-',
    'ENERGY_STORAGE': '--',
    'TIE_LINE': (0, (3, 10, 1, 10)),  # Corrected custom dash pattern
    'BTF_GENERATION' : '-'
}

#-------------------------------------------
#TECH_TYPE REDUCED Config
#-------------------------------------------
tech_type_desired_order_reduced = [
    'NON_WIND_SOLAR','SOLAR', 'WIND',#'TIE_LINE'
]

tech_type_reduced_colors = {
    'NON_WIND_SOLAR': custom_color_palette['Black'],
    'SOLAR': custom_color_palette['Yellow'], #was 'Cherry'
    'WIND': custom_color_palette['Leaf'],
    #'TIE_LINE': custom_color_palette['Dusk']
}

tech_type_custom_line_thickness_reduced = {
    'NON_WIND_SOLAR': 2.0,
    'SOLAR': 1.0,
    'WIND': 1.0,
}

tech_type_reduced_custom_line_styles = {
    'NON_WIND_SOLAR': '-',
    'SOLAR': (0, (3, 5, 1, 5, 1, 5)),
    'WIND': (0, (5, 1)),
    #'TIE_LINE': (0, (3, 10, 1, 10)) 
}

#-------------------------------------------
#FUEL_TYPE Config
##-------------------------------------------
# Define the desired order of the technology types
fuel_type_desired_order = [
    'COAL','GAS', 'DUAL_FUEL','HYDRO','OTHER',  'SOLAR' , 'WIND',  'UNKNOWN' , 'ENERGY_STORAGE','TIE_LINE'
]

fuel_type_colors = {
    'COAL': custom_color_palette['Black'],
    'GAS': custom_color_palette['Grey'],
    'DUAL_FUEL': custom_color_palette['Steel'],
    'HYDRO': custom_color_palette['Sky'],
    'OTHER': custom_color_palette['Clementine'],
    'SOLAR': custom_color_palette['Yellow'], #was 'Cherry'
    'WIND': custom_color_palette['Leaf'],
    'UNKNOWN': custom_color_palette['Moss'],
    'ENERGY_STORAGE': custom_color_palette['Ocean'],
    'TIE_LINE': custom_color_palette['Dusk'],
    'BTF_GENERATION' :  custom_color_palette['White']
}

original_fuel_type_color_map = fuel_type_colors.copy()

fuel_type_font_colors = {
    'COAL': 'white',
    'GAS' : 'white',
    'HYDRO': 'black',
    'DUAL_FUEL': 'black',
    'SIMPLE_CYCLE': 'black',
    'GAS_FIRED_STEAM': 'white',
    'OTHER': 'black',
    'SOLAR': 'black', #was white
    'WIND': 'black',
    'UNKNOWN': 'white',
    'ENERGY_STORAGE': 'white',
    'TIE_LINE':'white',
    'BTF_GENERATION' : 'white'
}

# Define custom line thickness for each TECH_TYPE
fuel_type_custom_line_thickness = {
    'COAL': 1.0,
    'GAS': 1.0,
    'DUAL_FUEL': 1.0,
    'HYDRO': 1.0,
    'OTHER': 1.0,
    'SOLAR': 2.0,
    'WIND': 2.0,
    'UNKNOWN': 1.0,
    'ENERGY_STORAGE': 1.0,
    'TIE_LINE' : 1.0,
    'BTF_GENERATION' : 1.0
}

fuel_type_markers = {
    'COAL': '>',
    'GAS': 's',
    'DUAL_FUEL': '^',
    'HYDRO': '<',
    'OTHER': 'x',
    'SOLAR': 'o',
    'WIND': 'h',
    'UNKNOWN': 'v',
    'ENERGY_STORAGE': '8',
    'TIE_LINE' : '*',
    'BTF_GENERATION' : 'o' 
}

fuel_type_custom_line_styles = {
    'COAL': '-',
    'GAS' : '--',
    'HYDRO': ':',
    'DUAL_FUEL': (0, (3, 5, 1, 5)),  # Example of a custom dash pattern
    'OTHER': (0, (3, 1, 1, 1)),
    'SOLAR': (0, (3, 5, 1, 5, 1, 5)),
    'WIND': (0, (5, 1)),
    'UNKNOWN': '-',
    'ENERGY_STORAGE': '--',
    'TIE_LINE': (0, (3, 10, 1, 10)),  # Corrected custom dash pattern
    'BTF_GENERATION' : '-'
}

#-------------------------------------------
#plotly
#-------------------------------------------

# import plotly.graph_objects as go

# # Define your default color scheme
# tech_type_colors = {
#     'SOLAR': 'blue', 
#     'COGENERATION': 'green',
#     'OTHER': 'coral',
#     'COAL': 'black',
#     'HYDRO': 'orange',
#     'GAS_FIRED_STEAM': 'purple',
#     'ENERGY_STORAGE': 'cyan',
#     'COMBINED_CYCLE': 'grey',
#     'DUAL_FUEL': 'yellow',
#     'SIMPLE_CYCLE': 'red',
#     'WIND': 'brown',
#     'UNKNOWN': 'gray'
# }

# # Define your trace data
# trace_data = [
#     {'x': [1, 2, 3], 'y': [4, 5, 6], 'name': 'Trace 1', 'marker': {'symbol': tech_type_markers['SOLAR'], 'size': 10}, 'line': {'width': custom_line_thickness['SOLAR'], 'color': tech_type_colors['SOLAR']}},
#     {'x': [1, 2, 3], 'y': [7, 8, 9], 'name': 'Trace 2', 'marker': {'symbol': tech_type_markers['COGENERATION'], 'size': 10}, 'line': {'width': custom_line_thickness['COGENERATION'], 'color': tech_type_colors['COGENERATION']}}
# ]

# # Create the figure
# fig = go.Figure(data=trace_data)

# # Set the template to your default template
# fig.update_layout(template='plotly_dark')

# # Show the plot
    # fig.show()

