import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import base64

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING (Modern Glassmorphic UI)
# ==========================================
st.set_page_config(
    page_title="PacketAI - NextGen Budget Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for College Presentation (Eye-Catching Design)
st.markdown("""

""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT (Data Persistence)
# ==========================================
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame([
        {"Date": "2026-10-01", "Category": "Needs", "Description": "House Rent", "Amount": 8000, "Type": "Expense"},
        {"Date": "2026-10-01", "Category": "Income", "Description": "Software Stipend", "Amount": 25000, "Type": "Income"},
        {"Date": "2026-10-02", "Category": "Wants", "Description": "College Canteen & Coffee", "Amount": 450, "Type": "Expense"},
        {"Date": "2026-10-03", "Category": "Needs", "Description": "Groceries", "Amount": 2200, "Type": "Expense"},
        {"Date": "2026-10-04", "Category": "Savings", "Description": "Mutual Fund SIP", "Amount": 3000, "Type": "Expense"},
        {"Date": "2026-10-05", "Category": "Wants", "Description": "Movie Night", "Amount": 600, "Type": "Expense"}
    ])

if 'ai_chat' not in st.session_state:
    st.session_state.ai_chat = [
        {"role": "assistant", "content": "👋 Vanakkam! I am **PacketAI**, your smart financial co-pilot. Ask me how to optimize your monthly expenses!"}
    ]

# ==========================================
# 3. HELPER & RULE-BASED AI FUNCTIONS
# ==========================================
def calculate_financial_health(income, expenses, savings):
    if income == 0:
        return 0, "No Data"
    
    savings_rate = (savings / income) * 100
    expense_ratio = (expenses / income) * 100
    
    score = 100
    if expense_ratio > 80:
        score -= 30
    elif expense_ratio > 60:
        score -= 15
        
    if savings_rate >= 20:
        score += 10
    else:
        score -= 10

    score = max(0, min(100, score))
    
    if score >= 80:
        status = "🟢 Excellent (A+)"
    elif score >= 60:
        status = "🟡 Good (B)"
    else:
        status = "🔴 Action Needed (C)"
        
    return score, status

def ai_smart_categorize(description):
    """Simple AI Rule Engine for Auto-Categorization"""
    desc = description.lower()
    if any(k in desc for k in ["rent", "groceries", "eb bill", "recharge", "bus", "petrol"]):
        return "Needs"
    elif any(k in desc for k in ["coffee", "movie", "swiggy", "dress", "zomato", "game"]):
        return "Wants"
    elif any(k in desc for k in ["sip", "stock", "fd", "savings", "gold"]):
        return "Savings"
    return "Others"

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://img.icons8.com/isometric-folders/100/brain.png", width=70)
st.sidebar.title("⚡ PacketAI Dashboard")
st.sidebar.caption("Smart Automated AI Financial Assistant")

menu = st.sidebar.radio(
    "Navigate Menu",
    ["📊 Dashboard & Analytics", "📝 Expense Entry & Smart AI OCR", "🔮 AI Financial Simulator", "🤖 Chat with PacketAI"]
)

# ==========================================
# 5. PAGE 1: DASHBOARD & ANALYTICS
# ==========================================
if menu == "📊 Dashboard & Analytics":
    st.title("📊 PacketAI - Smart Analytics")
    st.markdown("Real-time Overview of your monthly financial flows with AI Rule Engines.")

    # Calculate Totals
    df = st.session_state.transactions
    income_df = df[df["Type"] == "Income"]
    expense_df = df[df["Type"] == "Expense"]
    
    total_income = income_df["Amount"].sum()
    total_expense = expense_df["Amount"].sum()
    total_savings = total_income - total_expense

    health_score, health_status = calculate_financial_health(total_income, total_expense, total_savings)

    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", f"₹{total_income:,.2f}")
    col2.metric("Total Expense", f"₹{total_expense:,.2f}")
    col3.metric("Net Savings", f"₹{total_savings:,.2f}")
    col4.metric("AI Health Score", f"{health_score}/100", delta=health_status)

    st.markdown("---")

    # Layout Charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📌 50/30/20 Rule Breakdown")
        if not expense_df.empty:
            cat_fig = px.pie(
                expense_df, 
                names='Category', 
                values='Amount',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            cat_fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(cat_fig, use_container_width=True)
        else:
            st.info("No expense data available.")

    with col_chart2:
        st.subheader("📈 Monthly Cashflow")
        flow_df = df.groupby(["Category", "Type"])["Amount"].sum().reset_index()
        bar_fig = px.bar(
            flow_df, 
            x="Category", 
            y="Amount", 
            color="Type", 
            barmode="group",
            color_discrete_map={"Income": "#10b981", "Expense": "#f43f5e"}
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # AI Recommendation Box
    st.markdown("### 🤖 PacketAI Insights & Warnings")
    wants_spending = expense_df[expense_df["Category"] == "Wants"]["Amount"].sum()
    if total_income > 0 and (wants_spending / total_income) > 0.30:
        st.warning(f"⚠️ **High 'Wants' Spending Detected:** You spent **{((wants_spending/total_income)*100):.1f}%** on non-essentials! Recommended standard is under 30%.")
    else:
        st.success("✅ **Great Job!** Your spending fits well within the healthy budget boundaries.")

# ==========================================
# 6. PAGE 2: EXPENSE ENTRY & OCR SIMULATION
# ==========================================
elif menu == "📝 Expense Entry & Smart AI OCR":
    st.title("📝 Add Transactions & AI Receipt Parser")
    
    tab1, tab2 = st.tabs(["⚡ Manual / AI Smart Entry", "📄 Smart Receipt OCR Parser"])

    with tab1:
        st.subheader("Enter Transaction Details")
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_date = col1.date_input("Date")
            t_desc = col2.text_input("Description (e.g. Swiggy Lunch, Rent)")
            
            t_amount = col1.number_input("Amount (₹)", min_value=1.0, step=10.0)
            t_type = col2.selectbox("Type", ["Expense", "Income"])
            
            # AI Auto Category Recommendation
            auto_cat = ai_smart_categorize(t_desc) if t_desc else "Needs"
            t_cat = st.selectbox("Category (AI Suggested)", ["Needs", "Wants", "Savings", "Income"], index=["Needs", "Wants", "Savings", "Income"].index(auto_cat) if auto_cat in ["Needs", "Wants", "Savings", "Income"] else 0)

            submit = st.form_submit_button("Add Transaction")

            if submit:
                new_row = {"Date": str(t_date), "Category": t_cat, "Description": t_desc, "Amount": t_amount, "Type": t_type}
                st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Added: {t_desc} (₹{t_amount})")

    with tab2:
        st.subheader("📄 Simulated Smart OCR Receipt Text Extractor")
        st.caption("Paste your digital receipt/bill text below. PacketAI will scan keywords & auto-add them.")
        
        sample_receipt = st.text_area("Bill/Receipt Text", "Starbucks Coffee Shop\nTotal: 350 INR\nDate: 2026-10-01\nPaid via UPI")
        if st.button("Parse & Auto-Add Expense"):
            if "coffee" in sample_receipt.lower() or "starbucks" in sample_receipt.lower():
                new_row = {"Date": "2026-10-01", "Category": "Wants", "Description": "Starbucks Coffee (Parsed)", "Amount": 350, "Type": "Expense"}
                st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame([new_row])], ignore_index=True)
                st.balloons()
                st.success("Successfully Parsed & Categorized as 'Wants' (₹350)!")

    st.markdown("---")
    st.subheader("📋 All Records")
    st.dataframe(st.session_state.transactions, use_container_width=True)

# ==========================================
# 7. PAGE 3: AI FINANCIAL SIMULATOR
# ==========================================
elif menu == "🔮 AI Financial Simulator":
    st.title("🔮 Future Wealth & Scenario Simulator")
    st.markdown("Use this interactive simulator to show your college audience **how small savings grow over time!**")

    col1, col2 = st.columns(2)
    monthly_sav = col1.slider("Monthly Savings Investment (₹)", 500, 50000, 5000, 500)
    return_rate = col2.slider("Expected Annual Return Rate (%)", 1.0, 20.0, 12.0, 0.5)
    years = st.slider("Investment Horizon (Years)", 1, 30, 10)

    # Compound Interest Logic
    months = years * 12
    rate_per_month = (return_rate / 100) / 12
    
    data = []
    total_invested = 0
    current_val = 0
    
    for m in range(1, months + 1):
        total_invested += monthly_sav
        current_val = (current_val + monthly_sav) * (1 + rate_per_month)
        if m % 12 == 0:
            data.append({"Year": m // 12, "Total Invested": total_invested, "Future Value": round(current_val)})

    sim_df = pd.DataFrame(data)

    st.markdown(f"### 🚀 Result after {years} Years:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested", f"₹{total_invested:,.0f}")
    c2.metric("Estimated Future Value", f"₹{current_val:,.0f}")
    c3.metric("Estimated Wealth Gain", f"₹{(current_val - total_invested):,.0f}", delta="Growth")

    fig = px.line(sim_df, x="Year", y=["Total Invested", "Future Value"], title="Investment Projection Chart", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 8. PAGE 4: CHAT WITH PACKETAI
# ==========================================
elif menu == "🤖 Chat with PacketAI":
    st.title("🤖 PacketAI Financial Assistant Chat")
    st.caption("Ask questions about budgeting strategies, 50/30/20 rule, emergency funds, or SIPs.")

    for msg in st.session_state.ai_chat:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Ask PacketAI a question..."):
        st.session_state.ai_chat.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Smart Response Engine
        q = user_input.lower()
        if "50/30/20" in q or "rule" in q:
            ans = "The **50/30/20 Rule** suggests allocating your after-tax income to:\n- **50% Needs**: Essential expenses (Rent, Groceries, Bills)\n- **30% Wants**: Lifestyle/fun (Dining out, Movies)\n- **20% Savings**: SIPs, Emergency fund, Investments."
        elif "reduce" in q or "save" in q or "cut" in q:
            ans = "💡 **Top PacketAI Tip:** Track your daily micro-expenses (like daily snacks/coffee). Cutting ₹100/day saves ₹3,000/month, which equals ₹36,000/year invested in SIPs!"
        elif "health score" in q:
            ans = "Your **Financial Health Score** is calculated based on Expense-to-Income ratio and Savings percentage. Keeping expenses < 70% boosts your score to Green!"
        else:
            ans = f"Great question regarding **'{user_input}'**! PacketAI recommends automating your monthly savings first before spending on non-essentials ('Pay Yourself First' principle)."

        st.session_state.ai_chat.append({"role": "assistant", "content": ans})
        st.chat_message("assistant").write(ans)