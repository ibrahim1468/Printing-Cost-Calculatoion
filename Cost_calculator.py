import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="PrintCost Pro | Precision Calculator", layout="wide")

# --- DATA PRESETS ---
PAPER_SIZES = {
    "A4": (8.27, 11.69),
    "A5": (5.83, 8.27),
    "Legal": (8.5, 14.0),
    "Envelope (DL)": (4.33, 8.66),
    "Executive": (7.25, 10.5),
    "Custom": (0.0, 0.0)
}

PLATE_TYPES = {
    "Rota": 250.0,
    "Solna": 500.0,
    "GTO": 100.0,
    "Custom": 0.0
}

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🖨️ PrintCost Pro: Industrial Job Calculator")
st.markdown("---")

# --- SIDEBAR: GLOBAL SETTINGS ---
st.sidebar.header("Currency Settings")
currency = st.sidebar.selectbox("Currency", ["PKR (Rs.)", "INR (₹)", "USD ($)", "EUR (€)"])
curr_symbol = currency.split("(")[1].replace(")", "")

# --- INPUT SECTION ---
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    # A. Paper and Sheet Variables
    st.subheader("📦 1. Paper & Utilization")
    with st.expander("Paper Size & Quantity", expanded=True):
        p_col1, p_col2 = st.columns(2)
        
        with p_col1:
            paper_choice = st.selectbox("Select Paper Size", list(PAPER_SIZES.keys()))
            if paper_choice == "Custom":
                p_w = st.number_input("Unit Width (in)", value=8.0)
                p_h = st.number_input("Unit Height (in)", value=10.0)
            else:
                p_w, p_h = PAPER_SIZES[paper_choice]
                st.info(f"Dimensions: {p_w}\" x {p_h}\"")
            
            total_units = st.number_input("Total Units to Print", min_value=1, value=1000)
            
        with p_col2:
            sheet_w = st.number_input("Sheet Width (in)", value=25.0)
            sheet_h = st.number_input("Sheet Height (in)", value=36.0)
            price_per_sheet = st.number_input(f"Price per Full Sheet ({curr_symbol})", min_value=0.0, value=15.0)

        # Logic: Calculate best fit (Vertical vs Horizontal orientation)
        fit1 = (sheet_w // p_w) * (sheet_h // p_h)
        fit2 = (sheet_w // p_h) * (sheet_h // p_w)
        
        pcs_per_sheet = max(fit1, fit2)
        best_orientation = "Standard" if fit1 >= fit2 else "Rotated 90°"
        
        if pcs_per_sheet > 0:
            sheets_required = math.ceil(total_units / pcs_per_sheet)
        else:
            sheets_required = 0
            st.error("Error: Unit size is larger than the sheet size.")

        st.success(f"**Result:** {pcs_per_sheet} units per sheet ({best_orientation}). Total: **{sheets_required} sheets**.")

    # B. Printing Variables
    st.subheader("🎨 2. Printing & Plates")
    with st.expander("Printing Details", expanded=True):
        pr_col1, pr_col2 = st.columns(2)
        with pr_col1:
            plate_choice = st.selectbox("Plate Type", list(PLATE_TYPES.keys()))
            if plate_choice == "Custom":
                base_plate_cost = st.number_input("Custom Plate Cost", value=0.0)
            else:
                base_plate_cost = PLATE_TYPES[plate_choice]
                st.info(f"Base Cost: {curr_symbol}{base_plate_cost}")
            
            num_colors = st.number_input("Number of Colors", min_value=1, value=1)
            
        with pr_col2:
            print_rate_per_color = st.number_input(f"Print Rate/Color/Sheet ({curr_symbol})", value=0.05, format="%.3f")
        
        total_plate_cost = base_plate_cost * num_colors
        total_printing_cost = total_plate_cost + (print_rate_per_color * num_colors * sheets_required)

    # C, D, E. Finishing & Overheads
    st.subheader("🛠️ 3. Finishing & Overheads")
    with st.expander("Finishing, Packaging & Logistics", expanded=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("**Cutting & Die-Cutting**")
            cut_ops = st.number_input("Number of Cutting Ops", value=4)
            cut_rate = st.number_input(f"Cost per Operation ({curr_symbol})", value=10.0)
            die_cut_cost = st.number_input(f"Die-Cutting Fixed Cost ({curr_symbol})", value=0.0)
            
            st.markdown("**Binding**")
            binding_rate = st.number_input(f"Binding Cost per Unit ({curr_symbol})", value=0.20)
        
        with f_col2:
            st.markdown("**Packing**")
            packing_rate = st.number_input(f"Packing Cost per Sheet ({curr_symbol})", value=0.10)
            
            st.markdown("**Overheads**")
            overhead_fixed = st.number_input(f"Total Overhead/Fixed ({curr_symbol})", value=500.0)

    # Secondary Calculations
    total_paper_cost = sheets_required * price_per_sheet
    total_cutting_cost = (cut_ops * cut_rate) + die_cut_cost
    total_binding_cost = binding_rate * total_units
    total_packing_cost = packing_rate * sheets_required

with col2:
    # F. Margin & Final Calculation
    st.subheader("💰 Summary & Quotation")
    margin_percent = st.slider("Profit Margin (%)", 0, 100, 20)
    
    total_expenses = (
        total_paper_cost + total_printing_cost + total_cutting_cost + 
        total_binding_cost + total_packing_cost + overhead_fixed
    )
    margin_value = total_expenses * (margin_percent / 100)
    final_job_cost = total_expenses + margin_value
    cost_per_unit = final_job_cost / total_units if total_units > 0 else 0

    # Display Metrics
    st.metric("Total Job Cost", f"{curr_symbol}{final_job_cost:,.2f}")
    st.metric("Cost Per Unit", f"{curr_symbol}{cost_per_unit:,.2f}")

    # Cost Breakdown Chart
    breakdown_labels = ['Paper', 'Printing/Plates', 'Cutting', 'Binding', 'Packing', 'Overhead', 'Margin']
    breakdown_values = [total_paper_cost, total_printing_cost, total_cutting_cost, total_binding_cost, total_packing_cost, overhead_fixed, margin_value]
    
    fig_pie = go.Figure(data=[go.Pie(labels=breakdown_labels, values=breakdown_values, hole=.3)])
    fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

    # G. Sheet Utilization Visualization
    st.subheader("📐 Sheet Layout")
    fig_layout = go.Figure()
    # Parent Sheet
    fig_layout.add_shape(type="rect", x0=0, y0=0, x1=sheet_w, y1=sheet_h, line=dict(color="RoyalBlue", width=2), fillcolor="LightSkyBlue", opacity=0.2)
    
    # Fill with Units (Visualizing the 'Standard' orientation for simplicity)
    draw_w, draw_h = (p_w, p_h) if fit1 >= fit2 else (p_h, p_w)
    cols = int(sheet_w // draw_w)
    rows = int(sheet_h // draw_h)
    
    for r in range(rows):
        for c in range(cols):
            fig_layout.add_shape(type="rect", x0=c*draw_w, y0=r*draw_h, x1=(c+1)*draw_w, y1=(r+1)*draw_h, line=dict(color="Black", width=1))

    fig_layout.update_layout(xaxis_range=[-2, sheet_w+2], yaxis_range=[-2, sheet_h+2], height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_layout, use_container_width=True)

# --- FINAL DETAILED REPORT ---
st.markdown("---")
st.subheader("📋 Component-wise Breakdown Report")

report_df = pd.DataFrame({
    "Cost Category": ["Paper Material", "Printing & Plates", "Cutting & Die-Cutting", "Binding", "Packing", "Overheads", "TOTAL EXPENSES", "Profit Margin", "FINAL QUOTE"],
    "Formula / Details": [
        f"{sheets_required} sheets @ {price_per_sheet}/sheet",
        f"Plate({plate_choice}) + ({num_colors} colors * {sheets_required} sheets * {print_rate_per_color})",
        f"({cut_ops} ops * {cut_rate}) + {die_cut_cost} die-cut",
        f"{total_units} units @ {binding_rate}/unit",
        f"{sheets_required} sheets @ {packing_rate}/sheet",
        "Fixed operational costs",
        "Sum of all components",
        f"{margin_percent}% of expenses",
        "Total + Margin"
    ],
    "Amount": [
        f"{curr_symbol}{total_paper_cost:,.2f}",
        f"{curr_symbol}{total_printing_cost:,.2f}",
        f"{curr_symbol}{total_cutting_cost:,.2f}",
        f"{curr_symbol}{total_binding_cost:,.2f}",
        f"{curr_symbol}{total_packing_cost:,.2f}",
        f"{curr_symbol}{overhead_fixed:,.2f}",
        f"{curr_symbol}{total_expenses:,.2f}",
        f"{curr_symbol}{margin_value:,.2f}",
        f"{curr_symbol}{final_job_cost:,.2f}"
    ]
})

st.table(report_df)

# Download Button
csv = report_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Detailed Quotation", data=csv, file_name=f"quote_{paper_choice}_{total_units}.csv", mime='text/csv')
