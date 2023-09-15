import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup, SoupStrainer


# Collect data from the selected season
st.subheader("Select a Season")
year = st.selectbox("",(2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023))
st.write("You selected:", year)      
df = pd.read_csv("https://raw.githubusercontent.com/nzylakffa/weekly_stats/main/all_fantasy_stats_" + str(year) + ".csv")
df = df.rename(columns={'posteam': 'team',
                        'full_name': 'player'})

st.subheader("Select Weeks:")

weeks = st.slider(
    "The regular season was 17 weeks from 2016 to 2020. From 2021 on it's been 18 weeks. Weeks beyond that are playoffs.",
    value = [1, 18], max_value = 22, min_value = 1)

st.write("You've selected weeks ", weeks[0], " through ", weeks[1])

df = df[df['week'].between(weeks[0],weeks[1])]
df_total = df[df['week'].between(weeks[0],weeks[1])]
df_custom = df[df['week'].between(weeks[0],weeks[1])]
df_exp = df[df['week'].between(weeks[0],weeks[1])]


#########################
# Percent of Team Table #
#########################

st.subheader("Percent of Team Stats")

# These are the columns they're going to see
keep_custom = ['season', 'player', 'team', 'position', 'player_id', 'rec_attempt', 'pass_attempt_team', 'rush_attempt', 'rush_attempt_team',
               'rec_air_yards', 'rec_air_yards_team']

df_custom = df_custom[keep_custom]

grouped_df_custom = df_custom.groupby(['player_id', 'season', 'player', 'team', 'position']).agg({'rec_attempt' : 'sum',
                                                                                                'pass_attempt_team': 'sum',
                                                                                                'rush_attempt' : 'sum',
                                                                                                'rush_attempt_team' : 'sum',
                                                                                                'rec_air_yards' : 'sum',
                                                                                                'rec_air_yards_team' : 'sum',
                                                                                                'player_id' : 'count'})
# Rename player_id to games
grouped_df_custom = grouped_df_custom.rename(columns = {'player_id' : 'Games'})

grouped_df_custom['Target Share'] = grouped_df_custom['rec_attempt'] / grouped_df_custom['pass_attempt_team'] 
grouped_df_custom['Air Yards Share'] = grouped_df_custom['rec_air_yards'] / grouped_df_custom['rec_air_yards_team'] 
grouped_df_custom['Carry Share'] = grouped_df_custom['rush_attempt'] / grouped_df_custom['rush_attempt_team']

grouped_df_custom = grouped_df_custom[['Target Share', 'Air Yards Share', 'Carry Share', 'Games']]

# Select min games
min_games_p = st.number_input('**Set Minimum Games:** Remember your filter above! Make this smaller if you filtered on fewer weeks!!', min_value = 1, max_value = 22, value = 5)
st.write('Current Minimum Is: ', min_games_p)

# Filter on min games selected
grouped_df_custom = grouped_df_custom[grouped_df_custom['Games'] >= min_games_p]

grouped_df_custom = grouped_df_custom.reset_index()
grouped_df_custom = grouped_df_custom.drop('player_id', axis = 1)

grouped_df_custom = grouped_df_custom.style.format({
    'Target Share': '{:,.2%}'.format,
    'Air Yards Share': '{:,.2%}'.format,
    'Carry Share': '{:,.2%}'.format,
})

st.dataframe(grouped_df_custom, use_container_width = True, hide_index=True)

####################################
# Expected Fantasy Points Per Game #
####################################

st.subheader("Expected Fantasy Points Per Game")

# These are the columns they're going to see
keep_custom_exp = ['season', 'player', 'team', 'position', 'player_id', 'total_fantasy_points', 'total_fantasy_points_exp', 'total_fantasy_points_diff']

df_custom_exp = df_exp[keep_custom_exp]
  

grouped_df_custom_exp = df_custom_exp.groupby(['player_id', 'season', 'player', 'team', 'position']).agg({'total_fantasy_points' : 'mean',
                                                                                                          'total_fantasy_points_exp': 'mean',
                                                                                                          'total_fantasy_points_diff' : 'mean',
                                                                                                          'player_id' : 'count'})

grouped_df_custom_exp = grouped_df_custom_exp.rename(columns = {'total_fantasy_points': 'Fantasy Points',
                                                                'total_fantasy_points_exp': 'Exp Fantasy Points',
                                                                'total_fantasy_points_diff': 'Difference',
                                                                'player_id' : 'Games'})

# Select min games
min_games = st.number_input('**Set Minimum Games:** Remember your filter above! Make this smaller if you filtered on fewer weeks!', min_value = 1, max_value = 22, value = 5)
st.write('Current Minimum Is: ', min_games)

# Filter on min games selected
grouped_df_custom_exp = grouped_df_custom_exp[grouped_df_custom_exp['Games'] >= min_games]

grouped_df_custom_exp = grouped_df_custom_exp.reset_index()

grouped_df_custom_exp = grouped_df_custom_exp.drop('player_id', axis = 1)

# Rename columns
grouped_df_custom_exp = grouped_df_custom_exp.rename(columns = {'season': 'Season',
                                                                'player': 'Player',
                                                                'team': 'Team',
                                                                'position' : 'Pos'})

# Create position filter
pos = st.multiselect(
    "Filter Position:",
    ['QB', 'RB', 'WR', 'TE', 'SPEC'],
    ['QB', 'RB', 'WR', 'TE', 'SPEC'])

grouped_df_custom_exp = grouped_df_custom_exp[grouped_df_custom_exp['Pos'].isin(pos)]


st.dataframe(grouped_df_custom_exp, use_container_width = True, hide_index=True)

###############################
# Select Your Own Stats Table #
###############################

st.subheader("Select Your Own Stats")

# Per game or season total button
pg_total = st.radio(
    "Would you like per game or total season stats?",
    ["**Per Game**", "**Total Season**"])

# 3 stats at a time disclaimer
st.write(f"**You can only select one stat at a time!**")

if pg_total == "**Per Game**":
    stats = st.multiselect("DO NOT select: season, player, team or position. Those will be selected for you.",
                      list(df.columns.values),
                      ["rec_air_yards"])    
    # These are the columns they're going to see
    keep = ['season', 'player', 'team', 'position', 'player_id', 'rec_attempt']
    keep.extend(stats)
    df = df[keep]
    # Take the mean of the stat...also create games
    grouped_df = df.groupby(['player_id', 'season', 'player', 'team', 'position']).agg({stats[0] : 'mean',
                                                                                        'player_id' : 'count'})
    
    grouped_df = grouped_df.rename(columns = {'player_id': 'Games'})
    # Select min games
    min_games_c = st.number_input('**Set Minimum Games:** Remember your filter above!! Make this smaller if you filtered on fewer weeks!!', min_value = 1, max_value = 22, value = 5)
    st.write('Current Minimum Is: ', min_games_c)
    # Filter on min games selected
    grouped_df = grouped_df[grouped_df['Games'] >= min_games_c]
    # Round
    grouped_df = grouped_df.round(2)  
    # Reset the index
    grouped_df = grouped_df.reset_index()
    grouped_df = grouped_df.drop('player_id', axis = 1)
    # Create position filter
    pos_g = st.multiselect(
        "Filter Pos:",
        ['QB', 'RB', 'WR', 'TE', 'SPEC'],
        ['QB', 'RB', 'WR', 'TE', 'SPEC'])

    grouped_df = grouped_df[grouped_df['position'].isin(pos_g)]
    # Sort highest to lowest
    grouped_df = grouped_df.sort_values(by = stats[0], ascending=False)
    # Create Rank Column
    grouped_df['Rank'] = range(1,(len(grouped_df)+1))



    st.dataframe(grouped_df, use_container_width = True, hide_index=True)

else:
    stats_total = st.multiselect("DO NOT select: season, player, team or position. Those will be selected for you!",
                      list(df.columns.values),
                      ["rec_air_yards"])
    
        # These are the columns they're going to see
    keep_total = ['season', 'player', 'team', 'position', 'player_id', 'rec_attempt']
    keep_total.extend(stats_total)
    df_total = df_total[keep_total]
    # Take the sum of the stat...also create games
    grouped_df_total = df_total.groupby(['player_id', 'season', 'player', 'team', 'position']).agg({stats_total[0] : 'sum',
                                                                                                    'player_id' : 'count'})
    
    grouped_df_total = grouped_df_total.rename(columns = {'player_id': 'Games'})
    # Select min games
    min_games_c = st.number_input('**Set Minimum Games:** Remember your filter above!! Make this smaller if you filtered on fewer weeks!!', min_value = 1, max_value = 22, value = 5)
    st.write('Current Minimum Is: ', min_games_c)
    # Filter on min games selected
    grouped_df_total = grouped_df_total[grouped_df_total['Games'] >= min_games_c]
    # Round to two decimal spots    
    grouped_df_total = grouped_df_total.round(2)
    # Reset the index and drop the player_id column
    grouped_df_total = grouped_df_total.reset_index()
    grouped_df_total = grouped_df_total.drop('player_id', axis = 1)
    
    # Create position filter
    pos_t = st.multiselect(
        "Filter Pos: ",
        ['QB', 'RB', 'WR', 'TE', 'SPEC'],
        ['QB', 'RB', 'WR', 'TE', 'SPEC'])
    
    grouped_df_total = grouped_df_total[grouped_df_total['position'].isin(pos_t)]
    
    # Sort highest to lowest
    grouped_df_total = grouped_df_total.sort_values(by = stats_total[0], ascending=False)
    # Create Rank Column
    grouped_df_total['Rank'] = range(1,(len(grouped_df_total)+1))

    st.dataframe(grouped_df_total, use_container_width = True, hide_index=True)