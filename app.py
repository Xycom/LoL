import streamlit as st
import pandas as pd
from riot_api import get_puuid, get_match_ids, get_match_data
from analysis import analyze_player_data

st.set_page_config(
    page_title="Collegiate League Self Review Tool",
    page_icon="⚔️",
    layout="wide"
)

st.title("⚔️ Collegiate League Self Review Tool")
st.markdown("Analyze your League of Legends performance with Diamond baseline comparisons")

# Sidebar for input
with st.sidebar:
    st.header("Player Analysis")
    summoner_name = st.text_input(
        "Enter Summoner Name",
        placeholder="e.g., Faker",
        help="Enter your League of Legends summoner name"
    )
    
    num_matches = st.selectbox(
        "Number of Matches to Analyze",
        options=[5, 10, 15, 20],
        index=0,
        help="Select how many recent matches to analyze"
    )
    
    analyze_button = st.button(f"Analyze Last {num_matches} Matches", type="primary", use_container_width=True)

# Main content
if analyze_button:
    if not summoner_name:
        st.error("Please enter a summoner name")
    else:
        try:
            with st.spinner(f"Fetching data for {summoner_name}..."):
                # Get PUUID
                puuid = get_puuid(summoner_name)
                
                # Get match IDs
                match_ids = get_match_ids(puuid, count=num_matches)
                
                # Get match data
                match_data_list = []
                for match_id in match_ids:
                    match_data = get_match_data(match_id)
                    match_data_list.append(match_data)
                
                # Analyze data
                results = analyze_player_data(match_data_list, puuid)
            
            # Display results
            if results.empty:
                st.warning("No matches found for this player")
            else:
                st.success(f"✅ Analysis complete for {summoner_name}")
                
                # Filter to only the target player
                target_results = results[results["Summoner"] == summoner_name]
                
                if target_results.empty:
                    st.info(f"No data found for {summoner_name} in recent matches")
                else:
                    st.subheader(f"Performance Summary: {summoner_name}")
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    
                    avg_cspm = target_results["Avg CSPM"].mean()
                    avg_vs_diamond = target_results["Avg vs Diamond"].mean()
                    num_roles = len(target_results)
                    
                    with col1:
                        st.metric("Average CSPM", f"{avg_cspm:.2f}")
                    
                    with col2:
                        st.metric("Avg vs Diamond", f"{avg_vs_diamond:.2f}")
                    
                    with col3:
                        st.metric("Roles Played", num_roles)
                    
                    st.divider()
                    
                    # Display detailed results
                    st.subheader("Detailed Results by Role")
                    
                    # Format for display
                    display_df = target_results.copy()
                    display_df["Avg CSPM"] = display_df["Avg CSPM"].apply(lambda x: f"{x:.2f}")
                    display_df["Avg vs Diamond"] = display_df["Avg vs Diamond"].apply(lambda x: f"{x:.2f}")
                    display_df["Gold Baseline"] = display_df["Gold Baseline"].apply(lambda x: f"{x:.2f}")
                    display_df["Diamond Baseline"] = display_df["Diamond Baseline"].apply(lambda x: f"{x:.2f}")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                    )
                    
                    st.divider()
                    
                    # Coaching insights
                    st.subheader("💡 Coaching Insights")
                    
                    for _, row in target_results.iterrows():
                        role = row["Role"]
                        avg_cspm = row["Avg CSPM"]
                        diamond_baseline = row["Diamond Baseline"]
                        vs_diamond = row["Avg vs Diamond"]
                        
                        insight = f"**{role}**: {avg_cspm:.2f} CSPM"
                        
                        if vs_diamond < 0:
                            insight += f" ({vs_diamond:.2f} below Diamond baseline)"
                            st.warning(insight)
                        else:
                            insight += f" ({vs_diamond:+.2f} vs Diamond baseline)"
                            st.success(insight)
        
        except ValueError as e:
            st.error(f"❌ Summoner not found: {summoner_name}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please check your API key and summoner name")

# Footer with instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Enter your summoner name** in the sidebar
    2. **Click "Analyze Last 5 Matches"** to fetch and analyze your data
    3. **Review your performance** against Diamond baselines
    
    ### Metrics Explained
    - **Avg CSPM**: Average creep score per minute across recent matches
    - **Avg vs Diamond**: How your CSPM compares to Diamond rank baseline
    - **Roles Played**: Number of different roles in your recent matches
    
    ### Next Steps for Improvement
    - Focus on roles where you're significantly below Diamond
    - Use role-specific baselines to set farming goals
    - Monitor consistency across matches
    """)
