import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

def create_sankey_diagram(predictions, process_type="Secondary Production"):
    """Create a comprehensive Sankey diagram showing material flow: raw → process → end-of-life"""
    try:
        # Extract values from predictions
        energy = predictions.get('Energy_Use_MJ_per_kg', 100)
        emissions = predictions.get('Emission_kgCO2_per_kg', 10)
        water = predictions.get('Water_Use_l_per_kg', 50)
        recycled_content = predictions.get('Recycled_Content_pct', 30)
        reuse_potential = predictions.get('Reuse_Potential_score', 0.5) * 100
        circularity_index = predictions.get('Circularity_Index', 0.3) * 100
        
        # Adjust flows based on process type
        virgin_materials = 100 - recycled_content if process_type != "Primary Production" else 100
        recycling_input = recycled_content if process_type != "Primary Production" else 0
        
        # Define comprehensive nodes for material flow
        labels = [
            "Virgin Raw Materials",     # 0
            "Recycled Materials",       # 1 
            "Energy Inputs",            # 2
            "Water Inputs",             # 3
            "Transportation",           # 4
            "Production Process",       # 5
            "Metal Product",            # 6
            "CO₂ Emissions",            # 7
            "Wastewater",              # 8
            "Solid Waste",             # 9
            "Product Use",             # 10
            "Collection",              # 11
            "Recycling Process",       # 12
            "Reuse Applications",      # 13
            "Landfill",               # 14
            "Incineration"            # 15
        ]
        
        # Define comprehensive flows
        sources = [
            0, 1, 2, 3, 4,           # Inputs to production
            5, 5, 5, 5,              # Production outputs
            6, 10, 10, 10,           # Product lifecycle
            11, 11, 11               # End-of-life flows
        ]
        
        targets = [
            5, 5, 5, 5, 5,           # To production process
            6, 7, 8, 9,              # From production
            10, 11, 12, 13,          # Product use and collection
            12, 14, 15               # End-of-life destinations
        ]
        
        # Calculate flow values
        waste_factor = 15 + (emissions * 2)  # Higher emissions = more waste
        collection_rate = min(90, circularity_index + 20)  # Better circularity = better collection
        
        values = [
            virgin_materials,         # Virgin materials to production
            recycling_input,          # Recycled materials to production  
            energy / 2,              # Energy to production (scaled)
            water / 3,               # Water to production (scaled)
            10,                      # Transport to production
            100,                     # Production to product
            emissions * 8,           # Production to emissions
            water / 4,               # Production to wastewater
            waste_factor,            # Production to solid waste
            100,                     # Product to use phase
            collection_rate,         # Use to collection
            reuse_potential,         # Use to reuse
            100 - collection_rate - reuse_potential,  # Use to waste
            recycled_content,        # Collection to recycling
            (100 - collection_rate) * 0.6,  # Collection to landfill
            (100 - collection_rate) * 0.4   # Collection to incineration
        ]
        
        # Enhanced color scheme with better contrast for white text
        colors = [
            "#C0392B",  # Virgin Raw Materials - Dark Red
            "#27AE60",  # Recycled Materials - Dark Green 
            "#E67E22",  # Energy - Dark Orange
            "#2980B9",  # Water - Dark Blue
            "#8E44AD",  # Transportation - Dark Purple
            "#16A085",  # Production - Dark Teal
            "#F39C12",  # Product - Orange (darker than yellow)
            "#A93226",  # Emissions - Very Dark Red
            "#1F618D",  # Wastewater - Dark Blue
            "#935116",  # Solid Waste - Dark Brown
            "#196F3D",  # Product Use - Very Dark Green
            "#6C3483",  # Collection - Very Dark Purple
            "#117A65",  # Recycling - Very Dark Teal
            "#1B4F72",  # Reuse - Very Dark Blue
            "#5D6D7E",  # Landfill - Dark Gray
            "#922B21"   # Incineration - Very Dark Red
        ]
        
        # Create enhanced Sankey with improved text visibility
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=30,
                line=dict(color="#2C3E50", width=2),
                label=labels,
                color=colors,
                # Custom font styling for node labels
                hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>',
                x=[0.1, 0.1, 0.05, 0.05, 0.05, 0.3, 0.5, 0.4, 0.4, 0.4, 0.7, 0.85, 0.95, 0.95, 0.95, 0.95],
                y=[0.1, 0.3, 0.5, 0.7, 0.9, 0.5, 0.5, 0.2, 0.4, 0.6, 0.5, 0.5, 0.2, 0.4, 0.6, 0.8]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                # Improved link colors with better opacity for visibility
                color=[
                    "rgba(192, 57, 43, 0.4)",    # Virgin materials - darker
                    "rgba(39, 174, 96, 0.5)",    # Recycled materials - stronger
                    "rgba(230, 126, 34, 0.4)",   # Energy - darker orange
                    "rgba(41, 128, 185, 0.4)",   # Water - darker blue
                    "rgba(142, 68, 173, 0.4)",   # Transport - darker purple
                    "rgba(243, 156, 18, 0.7)",   # Production to product - more opaque
                    "rgba(169, 50, 38, 0.5)",    # Emissions - much darker
                    "rgba(31, 97, 141, 0.4)",    # Wastewater - darker
                    "rgba(147, 81, 22, 0.4)",    # Solid waste - darker brown
                    "rgba(25, 111, 61, 0.5)",    # Product use - darker green
                    "rgba(108, 52, 131, 0.4)",   # Collection - darker purple
                    "rgba(27, 79, 114, 0.4)",    # Reuse - darker blue
                    "rgba(93, 109, 126, 0.4)",   # To waste - darker gray
                    "rgba(17, 122, 101, 0.6)",   # Recycling - darker teal
                    "rgba(93, 109, 126, 0.5)",   # Landfill - darker gray
                    "rgba(146, 43, 33, 0.5)"     # Incineration - darker red
                ],
                # Add hover template for links
                hovertemplate='<b>Flow:</b> %{source.label} → %{target.label}<br><b>Volume:</b> %{value:.1f}<extra></extra>'
            )
        )])
        
        # Format title to handle long process types
        title_text = f"Complete Material Flow Analysis<br><sub>{process_type}</sub>"
        
        fig.update_layout(
            title=dict(
                text=title_text,
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color="#2C3E50", family="Arial Black")
            ),
            # Improved font settings for node labels
            font=dict(
                size=12,
                color="#FFFFFF",  # White text for contrast
                family="Arial Bold"
            ),
            height=600,
            margin=dict(t=100, l=30, r=30, b=30),
            paper_bgcolor="#F8F9FA",  # Light gray background
            plot_bgcolor="#F8F9FA",
            # Add annotations for better readability
            annotations=[
                dict(
                    text="🔄 Material flows from left to right • Node size = Flow volume",
                    showarrow=False,
                    x=0.5, y=-0.05,
                    xref="paper", yref="paper",
                    font=dict(size=11, color="#7F8C8D"),
                    xanchor="center"
                )
            ]
        )
        
        return fig
    
    except Exception as e:
        # Enhanced fallback chart with better text visibility
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Sankey diagram temporarily unavailable<br>Error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=16, color="#FFFFFF", family="Arial Bold"),
            bgcolor="#E74C3C",  # Red background for white text
            bordercolor="#C0392B",
            borderwidth=2,
            showarrow=False
        )
        fig.update_layout(
            title=dict(
                text="Complete Material Flow Analysis", 
                font=dict(size=18, color="#2C3E50")
            ),
            height=450,
            paper_bgcolor="#F8F9FA",
            plot_bgcolor="#FFFFFF"
        )
        return fig

def create_energy_comparison(comparison_df):
    """Create energy comparison bar chart"""
    try:
        if comparison_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No comparison data available", 
                              xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        fig = px.bar(
            comparison_df,
            x='Pathway',
            y='Energy (MJ/kg)',
            title='Energy Consumption by Production Pathway',
            color='Energy (MJ/kg)',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_title="Production Pathway",
            yaxis_title="Energy Use (MJ/kg)",
            height=400,
            showlegend=False
        )
        
        # Add value labels on bars
        for i, row in comparison_df.iterrows():
            fig.add_annotation(
                x=row['Pathway'],
                y=row['Energy (MJ/kg)'],
                text=f"{row['Energy (MJ/kg)']:.1f}",
                showarrow=False,
                yshift=10
            )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Energy chart error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#FFFFFF", family="Arial Bold"),
            bgcolor="#E74C3C",
            bordercolor="#C0392B",
            borderwidth=2,
            showarrow=False
        )
        fig.update_layout(
            title=dict(text="Energy Comparison", font=dict(color="#2C3E50")), 
            height=400,
            paper_bgcolor="#F8F9FA"
        )
        return fig

def create_emissions_comparison(comparison_df):
    """Create emissions comparison bar chart"""
    try:
        if comparison_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No comparison data available", 
                              xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        fig = px.bar(
            comparison_df,
            x='Pathway',
            y='Emissions (kgCO2/kg)',
            title='CO₂ Emissions by Production Pathway',
            color='Emissions (kgCO2/kg)',
            color_continuous_scale='Oranges'
        )
        
        fig.update_layout(
            xaxis_title="Production Pathway",
            yaxis_title="CO₂ Emissions (kg/kg)",
            height=400,
            showlegend=False
        )
        
        # Add value labels on bars
        for i, row in comparison_df.iterrows():
            fig.add_annotation(
                x=row['Pathway'],
                y=row['Emissions (kgCO2/kg)'],
                text=f"{row['Emissions (kgCO2/kg)']:.2f}",
                showarrow=False,
                yshift=10
            )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Emissions chart error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#FFFFFF", family="Arial Bold"),
            bgcolor="#E74C3C",
            bordercolor="#C0392B",
            borderwidth=2,
            showarrow=False
        )
        fig.update_layout(
            title=dict(text="Emissions Comparison", font=dict(color="#2C3E50")), 
            height=400,
            paper_bgcolor="#F8F9FA"
        )
        return fig

def create_circularity_comparison(comparison_df):
    """Create circularity metrics comparison radar chart"""
    try:
        if comparison_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No comparison data available", 
                              xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Normalize circularity metrics to 0-100 scale for better visualization
        metrics = ['Circularity Index', 'Recycled Content (%)', 'Reuse Potential']
        
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, row in comparison_df.iterrows():
            values = [
                row['Circularity Index'] * 100,  # Convert to percentage
                row['Recycled Content (%)'],
                row['Reuse Potential'] * 100     # Convert to percentage
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the polygon
                theta=metrics + [metrics[0]],
                fill='toself',
                name=row['Pathway'],
                line_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Circularity Metrics Comparison",
            height=400
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Circularity chart error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#FFFFFF", family="Arial Bold"),
            bgcolor="#E74C3C",
            bordercolor="#C0392B",
            borderwidth=2,
            showarrow=False
        )
        fig.update_layout(
            title=dict(text="Circularity Comparison", font=dict(color="#2C3E50")), 
            height=400,
            paper_bgcolor="#F8F9FA"
        )
        return fig

def create_water_usage_chart(comparison_df):
    """Create water usage comparison chart"""
    try:
        if comparison_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No comparison data available", 
                              xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        fig = px.bar(
            comparison_df,
            x='Pathway',
            y='Water (L/kg)',
            title='Water Usage by Production Pathway',
            color='Water (L/kg)',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Production Pathway",
            yaxis_title="Water Use (L/kg)",
            height=400,
            showlegend=False
        )
        
        # Add value labels on bars
        for i, row in comparison_df.iterrows():
            fig.add_annotation(
                x=row['Pathway'],
                y=row['Water (L/kg)'],
                text=f"{row['Water (L/kg)']:.1f}",
                showarrow=False,
                yshift=10
            )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Water chart error: {str(e)}", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(title="Water Usage Comparison", height=400)
        return fig

def create_environmental_summary_chart(predictions):
    """Create a summary chart of all environmental indicators"""
    try:
        # Extract environmental values
        energy = predictions.get('Energy_Use_MJ_per_kg', 0)
        emissions = predictions.get('Emission_kgCO2_per_kg', 0)
        water = predictions.get('Water_Use_l_per_kg', 0)
        
        # Normalize values for comparison (scale to 0-100)
        max_energy = 200  # Assumed max for normalization
        max_emissions = 20
        max_water = 100
        
        normalized_values = [
            (energy / max_energy) * 100,
            (emissions / max_emissions) * 100,
            (water / max_water) * 100
        ]
        
        labels = ['Energy Use', 'CO₂ Emissions', 'Water Use']
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=normalized_values,
                marker_color=['#FF6B6B', '#FFA500', '#4169E1'],
                text=[f'{energy:.1f} MJ/kg', 
                      f'{emissions:.2f} kgCO₂/kg', 
                      f'{water:.1f} L/kg'],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Environmental Impact Summary',
            xaxis_title='Environmental Indicators',
            yaxis_title='Normalized Impact (0-100)',
            height=400
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Summary chart error: {str(e)}", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        fig.update_layout(title="Environmental Summary", height=400)
        return fig

def create_metal_comparison_chart(comparison_data=None):
    """Create interactive bar chart comparing Energy, Emissions, Water across different metals"""
    try:
        # Sample data if none provided
        if comparison_data is None:
            metals = ['Aluminum', 'Steel', 'Copper', 'Zinc', 'Lead', 'Nickel']
            comparison_data = pd.DataFrame({
                'Metal': metals,
                'Energy_Use_MJ_per_kg': [150, 120, 80, 65, 45, 180],
                'Emission_kgCO2_per_kg': [12, 8, 5, 4, 3, 15],
                'Water_Use_l_per_kg': [60, 45, 35, 25, 20, 70]
            })
        
        # Create subplot with secondary y-axis
        fig = go.Figure()
        
        # Add Energy bars
        fig.add_trace(go.Bar(
            name='Energy Use (MJ/kg)',
            x=comparison_data['Metal'],
            y=comparison_data['Energy_Use_MJ_per_kg'],
            yaxis='y',
            marker_color='#FF6B6B',
            text=comparison_data['Energy_Use_MJ_per_kg'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Energy: %{y:.1f} MJ/kg<extra></extra>'
        ))
        
        # Add Emissions bars  
        fig.add_trace(go.Bar(
            name='CO₂ Emissions (kg/kg)',
            x=comparison_data['Metal'],
            y=comparison_data['Emission_kgCO2_per_kg'],
            yaxis='y2',
            marker_color='#FFA500',
            text=comparison_data['Emission_kgCO2_per_kg'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Emissions: %{y:.1f} kgCO₂/kg<extra></extra>'
        ))
        
        # Add Water bars
        fig.add_trace(go.Bar(
            name='Water Use (L/kg)',
            x=comparison_data['Metal'], 
            y=comparison_data['Water_Use_l_per_kg'],
            yaxis='y3',
            marker_color='#4169E1',
            text=comparison_data['Water_Use_l_per_kg'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Water: %{y:.1f} L/kg<extra></extra>'
        ))
        
        # Update layout with multiple y-axes
        fig.update_layout(
            title=dict(
                text="Environmental Impact Comparison Across Metals",
                x=0.5,
                font=dict(size=16, color="#2C3E50")
            ),
            xaxis=dict(title="Metal Type", titlefont=dict(size=14)),
            yaxis=dict(
                title="Energy Use (MJ/kg)", 
                titlefont=dict(color="#FF6B6B", size=14),
                tickfont=dict(color="#FF6B6B"),
                side="left"
            ),
            yaxis2=dict(
                title="CO₂ Emissions (kg/kg)",
                titlefont=dict(color="#FFA500", size=14),
                tickfont=dict(color="#FFA500"),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            yaxis3=dict(
                title="Water Use (L/kg)",
                titlefont=dict(color="#4169E1", size=14), 
                tickfont=dict(color="#4169E1"),
                anchor="free",
                overlaying="y",
                side="right",
                position=0.95
            ),
            barmode='group',
            height=450,
            margin=dict(t=80, l=60, r=80, b=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right", 
                x=1
            ),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Metal comparison chart unavailable<br>Error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#E74C3C"),
            showarrow=False
        )
        fig.update_layout(title="Metal Environmental Comparison", height=400)
        return fig

def create_circularity_scatter_plot(data_points=None):
    """Create interactive scatter plot of Circularity Index vs Recycled Content"""
    try:
        # Generate sample data if none provided
        if data_points is None:
            np.random.seed(42)
            n_points = 50
            
            # Create realistic relationships
            recycled_content = np.random.normal(40, 20, n_points)
            recycled_content = np.clip(recycled_content, 0, 100)
            
            # Circularity generally increases with recycled content but with variation
            circularity_base = (recycled_content / 100) * 0.7 + 0.1
            circularity_noise = np.random.normal(0, 0.1, n_points)
            circularity_index = np.clip(circularity_base + circularity_noise, 0, 1)
            
            # Add categorical data
            metals = np.random.choice(['Aluminum', 'Steel', 'Copper', 'Zinc', 'Lead'], n_points)
            processes = np.random.choice(['Primary', 'Secondary', 'Hybrid'], n_points)
            
            data_points = pd.DataFrame({
                'Recycled_Content_pct': recycled_content,
                'Circularity_Index': circularity_index,
                'Metal': metals,
                'Process_Type': processes,
                'Reuse_Potential': np.random.uniform(0, 1, n_points)
            })
        
        # Create scatter plot with color coding
        fig = px.scatter(
            data_points,
            x='Recycled_Content_pct',
            y='Circularity_Index',
            color='Metal',
            size='Reuse_Potential',
            symbol='Process_Type',
            title="Circularity Performance Analysis",
            labels={
                'Recycled_Content_pct': 'Recycled Content (%)',
                'Circularity_Index': 'Circularity Index',
                'Reuse_Potential': 'Reuse Potential'
            },
            hover_data=['Process_Type'],
            size_max=20
        )
        
        # Add trend line
        from sklearn.linear_model import LinearRegression
        X = np.array(data_points['Recycled_Content_pct']).reshape(-1, 1)
        y = np.array(data_points['Circularity_Index'])
        
        reg = LinearRegression().fit(X, y)
        trend_x = np.linspace(data_points['Recycled_Content_pct'].min(), 
                             data_points['Recycled_Content_pct'].max(), 100)
        trend_y = reg.predict(trend_x.reshape(-1, 1))
        
        fig.add_trace(go.Scatter(
            x=trend_x,
            y=trend_y,
            mode='lines',
            name=f'Trend (R² = {reg.score(X, y):.3f})',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='Trend Line<extra></extra>'
        ))
        
        # Add target zones
        fig.add_shape(
            type="rect",
            x0=60, y0=0.7, x1=100, y1=1,
            fillcolor="rgba(46, 204, 113, 0.2)",
            line=dict(color="rgba(46, 204, 113, 0.8)", width=2),
            layer="below"
        )
        
        fig.add_annotation(
            x=80, y=0.85,
            text="🎯 Target Zone<br>High Circularity",
            showarrow=False,
            font=dict(color="green", size=12),
            bgcolor="rgba(255,255,255,0.8)"
        )
        
        # Update layout
        fig.update_layout(
            height=450,
            xaxis=dict(
                title="Recycled Content (%)",
                range=[-5, 105],
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title="Circularity Index",
                range=[-0.05, 1.05],
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            title=dict(
                x=0.5,
                font=dict(size=16, color="#2C3E50")
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            margin=dict(t=80, l=60, r=120, b=60)
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Circularity scatter plot unavailable<br>Error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#E74C3C"),
            showarrow=False
        )
        fig.update_layout(title="Circularity vs Recycled Content Analysis", height=400)
        return fig

def create_comprehensive_dashboard(predictions, comparison_df=None):
    """Create a comprehensive dashboard with multiple visualizations"""
    try:
        from plotly.subplots import make_subplots
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Environmental Impact Summary",
                "Circularity Metrics",
                "Process Efficiency",
                "Sustainability Score"
            ),
            specs=[[{"type": "bar"}, {"type": "scatterpolar"}],
                   [{"type": "scatter"}, {"type": "indicator"}]]
        )
        
        # Environmental Impact Bar Chart
        env_metrics = ['Energy', 'Emissions', 'Water']
        env_values = [
            predictions.get('Energy_Use_MJ_per_kg', 0),
            predictions.get('Emission_kgCO2_per_kg', 0) * 10,  # Scale for visibility
            predictions.get('Water_Use_l_per_kg', 0)
        ]
        
        fig.add_trace(
            go.Bar(x=env_metrics, y=env_values, 
                   marker_color=['#FF6B6B', '#FFA500', '#4169E1'],
                   name="Environmental"),
            row=1, col=1
        )
        
        # Circularity Radar Chart
        circ_metrics = ['Circularity Index', 'Recycled Content', 'Reuse Potential']
        circ_values = [
            predictions.get('Circularity_Index', 0) * 100,
            predictions.get('Recycled_Content_pct', 0),
            predictions.get('Reuse_Potential_score', 0) * 100
        ]
        
        fig.add_trace(
            go.Scatterpolar(
                r=circ_values + [circ_values[0]],
                theta=circ_metrics + [circ_metrics[0]],
                fill='toself',
                name="Circularity",
                marker_color='#2ECC71'
            ),
            row=1, col=2
        )
        
        # Process Efficiency Scatter
        if comparison_df is not None and not comparison_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=comparison_df['Energy (MJ/kg)'],
                    y=comparison_df['Circularity Index'],
                    mode='markers+text',
                    text=comparison_df['Pathway'],
                    textposition='top center',
                    marker=dict(size=12, color='#9B59B6'),
                    name="Pathways"
                ),
                row=2, col=1
            )
        
        # Overall Sustainability Score
        sustainability_score = (
            (1 - min(predictions.get('Energy_Use_MJ_per_kg', 200) / 200, 1)) * 25 +
            (1 - min(predictions.get('Emission_kgCO2_per_kg', 20) / 20, 1)) * 25 +
            (1 - min(predictions.get('Water_Use_l_per_kg', 100) / 100, 1)) * 25 +
            (predictions.get('Circularity_Index', 0) * 25)
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=sustainability_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Sustainability Score"},
                delta={'reference': 75},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            title_text="LCA Performance Dashboard",
            title_x=0.5,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ Dashboard unavailable<br>Error: {str(e)}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(size=14, color="#E74C3C"),
            showarrow=False
        )
        fig.update_layout(title="LCA Performance Dashboard", height=600)
        return fig