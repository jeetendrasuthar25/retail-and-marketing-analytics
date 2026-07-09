# Python Dash Dashboard (Interactive Web App)
# Install required packages
# pip install dash plotly dash-bootstrap-components

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load processed data
df_sales = pd.read_csv('data/processed/cleaned_retail_sales.csv')
df_sales['Order_Date'] = pd.to_datetime(df_sales['Order_Date'])

rfm = pd.read_csv('data/processed/customer_segments.csv')
monthly_kpis = pd.read_csv('data/processed/monthly_kpis.csv')

# Calculate KPIs
kpis = {
    'Total_Revenue': df_sales['Sales'].sum(),
    'Total_Customers': df_sales['Customer_ID'].nunique(),
    'Avg_Order_Value': df_sales.groupby('Order_ID')['Sales'].sum().mean(),
    'CLV_to_CAC_Ratio': rfm['Monetary'].mean() / 50  # Assuming CAC = $50
}

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Retail & Marketing Analytics Dashboard", 
                        className="text-center mb-4"), width=12)
    ]),
    
    # KPI Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"${kpis['Total_Revenue']:,.0f}", className="card-title"),
                html.P("Total Revenue", className="card-text")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{kpis['Total_Customers']:,}", className="card-title"),
                html.P("Total Customers", className="card-text")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"${kpis['Avg_Order_Value']:,.2f}", className="card-title"),
                html.P("Avg Order Value", className="card-text")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{kpis['CLV_to_CAC_Ratio']:.2f}x", className="card-title"),
                html.P("CLV/CAC Ratio", className="card-text")
            ])
        ]), width=3)
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col(dcc.Graph(id='revenue-trend'), width=8),
        dbc.Col(dcc.Graph(id='customer-segments'), width=4)
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col(dcc.Graph(id='category-performance'), width=6),
        dbc.Col(dcc.Graph(id='regional-sales'), width=6)
    ])
    
], fluid=True)

# Callbacks for interactivity
@app.callback(
    Output('revenue-trend', 'figure'),
    Input('revenue-trend', 'id')
)
def update_revenue_trend(_):
    fig = px.line(monthly_kpis, x='YearMonth', y='Revenue',
                  title='Monthly Revenue Trend',
                  markers=True,
                  labels={'YearMonth': 'Month', 'Revenue': 'Revenue ($)'})
    fig.update_xaxes(tickangle=45)
    return fig

@app.callback(
    Output('customer-segments', 'figure'),
    Input('customer-segments', 'id')
)
def update_segments(_):
    if 'Cluster_Name' in rfm.columns:
        segment_counts = rfm['Cluster_Name'].value_counts()
    else:
        segment_counts = rfm['Customer_Segment'].value_counts()
    
    fig = px.pie(values=segment_counts.values, names=segment_counts.index,
                 title='Customer Segments',
                 hole=0.4)
    return fig

@app.callback(
    Output('category-performance', 'figure'),
    Input('category-performance', 'id')
)
def update_category(_):
    if 'Product_Category' in df_sales.columns:
        category_sales = df_sales.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=False)
        fig = px.bar(x=category_sales.index, y=category_sales.values,
                     title='Revenue by Category',
                     labels={'x': 'Category', 'y': 'Revenue ($)'})
    else:
        fig = px.bar(title='Category data not available')
    return fig

@app.callback(
    Output('regional-sales', 'figure'),
    Input('regional-sales', 'id')
)
def update_regional(_):
    if 'Region' in df_sales.columns:
        regional_sales = df_sales.groupby('Region')['Revenue'].sum()
        fig = px.pie(values=regional_sales.values, names=regional_sales.index,
                     title='Revenue by Region')
    else:
        fig = px.pie(title='Regional data not available')
    return fig

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=8050)