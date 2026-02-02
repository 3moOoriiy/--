import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

# Import plotly with error handling
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة الأرباح والخسائر",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS مخصص للتصميم المطابق للصورة بالضبط
st.markdown("""
<style>
    /* إخفاء العناصر الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* الخلفية العامة */
    .main {
        background-color: #f0f2f6;
        direction: rtl;
        text-align: right;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Header الأزرق الغامق */
    .custom-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 22px 40px;
        color: white;
        text-align: right;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        display: inline-block;
    }
    
    .custom-header .icon {
        font-size: 24px;
        margin-left: 10px;
    }
    
    .custom-header p {
        margin: 5px 0 0 0;
        font-size: 12px;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Content Area */
    .content-wrapper {
        padding: 25px 40px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: white;
        padding: 0 40px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 16px 28px;
        background-color: transparent;
        border-bottom: 2px solid transparent;
        color: #6b7280;
        font-weight: 500;
        font-size: 14px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom-color: #2563eb;
        color: #1f2937;
    }
    
    /* Filter Buttons */
    .stButton button {
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 9px 18px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    /* الكروت */
    .metric-card {
        background: white;
        padding: 24px 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e5e7eb;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-label {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 14px;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        line-height: 1;
    }
    
    .metric-value.green {
        color: #10b981;
    }
    
    .metric-value.red {
        color: #ef4444;
    }
    
    .metric-unit {
        font-size: 14px;
        margin-right: 4px;
        font-weight: 600;
    }
    
    /* Charts Container */
    .chart-box {
        background: white;
        padding: 22px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
    }
    
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 18px;
        color: #1f2937;
        text-align: right;
    }
    
    /* Form styling */
    .stSelectbox, .stNumberInput, .stTextArea, .stDateInput {
        font-size: 14px;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 13px;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .content-wrapper {
            padding: 20px;
        }
        .custom-header {
            padding: 18px 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# تهيئة البيانات في Session State
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'current_period' not in st.session_state:
    st.session_state.current_period = 'all'

# دوال مساعدة
def load_transactions():
    """تحميل المعاملات من ملف JSON"""
    try:
        with open('transactions.json', 'r', encoding='utf-8') as f:
            st.session_state.transactions = json.load(f)
    except FileNotFoundError:
        st.session_state.transactions = []

def save_transactions():
    """حفظ المعاملات في ملف JSON"""
    with open('transactions.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.transactions, f, ensure_ascii=False, indent=2)

def add_transaction(trans_type, category, amount, date, description):
    """إضافة معاملة جديدة"""
    transaction = {
        'id': len(st.session_state.transactions) + 1,
        'type': trans_type,
        'category': category,
        'amount': float(amount),
        'date': date.strftime('%Y-%m-%d'),
        'description': description,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.transactions.append(transaction)
    save_transactions()

def delete_transaction(trans_id):
    """حذف معاملة"""
    st.session_state.transactions = [t for t in st.session_state.transactions if t['id'] != trans_id]
    save_transactions()

def get_filtered_transactions(period='all'):
    """فلترة المعاملات حسب الفترة"""
    if not st.session_state.transactions:
        return []
    
    df = pd.DataFrame(st.session_state.transactions)
    df['date'] = pd.to_datetime(df['date'])
    
    today = pd.Timestamp.now().normalize()
    
    if period == 'today':
        df = df[df['date'] >= today]
    elif period == 'week':
        week_ago = today - timedelta(days=7)
        df = df[df['date'] >= week_ago]
    elif period == 'month':
        df = df[(df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)]
    
    return df.to_dict('records') if not df.empty else []

def calculate_stats(transactions):
    """حساب الإحصائيات"""
    if not transactions:
        return 0, 0, 0, 0
    
    revenues = [t['amount'] for t in transactions if t['type'] == 'revenue']
    expenses = [t['amount'] for t in transactions if t['type'] == 'expense']
    
    total_revenue = sum(revenues)
    total_expense = sum(expenses)
    net_profit = total_revenue - total_expense
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return total_revenue, total_expense, net_profit, profit_margin

# تحميل البيانات عند البداية
load_transactions()

# Header مخصص
st.markdown("""
<div class="custom-header">
    <span class="icon">📊</span><h1 style="display: inline;">نظام إدارة الأرباح والخسائر</h1>
    <p>تتبع ميزانيتك وأرباحك بشكل احترافي</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["لوحة التحكم", "المعاملات", "التقارير", "إضافة معاملة"])

# Tab 1: لوحة التحكم
with tab1:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # Filter Buttons في صف واحد على اليمين
    col_space, col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([4, 1, 1.2, 1.2, 0.8])
    
    with col_btn4:
        if st.button("الكل", key="all"):
            st.session_state.current_period = 'all'
            st.rerun()
    with col_btn3:
        if st.button("هذا الشهر", key="month"):
            st.session_state.current_period = 'month'
            st.rerun()
    with col_btn2:
        if st.button("هذا الأسبوع", key="week"):
            st.session_state.current_period = 'week'
            st.rerun()
    with col_btn1:
        if st.button("اليوم", key="today"):
            st.session_state.current_period = 'today'
            st.rerun()
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # الحصول على المعاملات المفلترة
    filtered_trans = get_filtered_transactions(st.session_state.current_period)
    total_revenue, total_expense, net_profit, profit_margin = calculate_stats(filtered_trans)
    
    # الكروت الرئيسية - 4 كروت متساوية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">إجمالي الإيرادات</div>
            <div class="metric-value green">{total_revenue:.2f} <span class="metric-unit">ج.م</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">إجمالي المصروفات</div>
            <div class="metric-value red">{total_expense:.2f} <span class="metric-unit">ج.م</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        profit_color = "green" if net_profit >= 0 else "red"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">صافي الربح/الخسارة</div>
            <div class="metric-value {profit_color}">{net_profit:.2f} <span class="metric-unit">ج.م</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        margin_color = "green" if profit_margin >= 0 else "red"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">نسبة الربح</div>
            <div class="metric-value {margin_color}">{profit_margin:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)
    
    # الرسوم البيانية
    if filtered_trans and PLOTLY_AVAILABLE:
        col_chart1, col_chart2 = st.columns([1, 1])
        
        with col_chart1:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 الإيرادات vs المصروفات (آخر 7 أيام)</div>', unsafe_allow_html=True)
            
            # إعداد البيانات لآخر 7 أيام
            dates = pd.date_range(end=pd.Timestamp.now(), periods=7).date
            df = pd.DataFrame(filtered_trans)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            revenue_data = []
            expense_data = []
            
            for date in dates:
                rev = df[(df['type'] == 'revenue') & (df['date'] == date)]['amount'].sum()
                exp = df[(df['type'] == 'expense') & (df['date'] == date)]['amount'].sum()
                revenue_data.append(rev)
                expense_data.append(exp)
            
            # رسم بياني خطي
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(7)),
                y=revenue_data,
                name='الإيرادات',
                line=dict(color='#10b981', width=2),
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            fig.add_trace(go.Scatter(
                x=list(range(7)),
                y=expense_data,
                name='المصروفات',
                line=dict(color='#ef4444', width=2),
                mode='lines',
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)'
            ))
            fig.update_layout(
                height=280,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=40, r=20, t=10, b=40),
                xaxis=dict(showgrid=True, gridcolor='#f3f4f6', tickmode='linear'),
                yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
                font=dict(size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🥧 توزيع الإيرادات والمصروفات</div>', unsafe_allow_html=True)
            
            # رسم دائري
            if total_revenue > 0 or total_expense > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['الإيرادات', 'المصروفات'],
                    values=[total_revenue, total_expense],
                    marker=dict(colors=['#10b981', '#ef4444']),
                    hole=0.5,
                    textinfo='label+percent',
                    textposition='outside',
                    textfont=dict(size=12)
                )])
                fig.update_layout(
                    height=280,
                    showlegend=False,
                    margin=dict(l=20, r=20, t=10, b=20),
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات لعرضها")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif not filtered_trans:
        st.info("📭 لا توجد معاملات في هذه الفترة. ابدأ بإضافة معاملاتك من تبويب 'إضافة معاملة'")
    elif not PLOTLY_AVAILABLE:
        st.warning("⚠️ مكتبة Plotly غير متاحة. الرسوم البيانية معطلة مؤقتاً.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: المعاملات
with tab2:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        # فلاتر
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            filter_type = st.selectbox(
                "نوع المعاملة",
                ["all", "revenue", "expense"],
                format_func=lambda x: {"all": "الكل", "revenue": "إيرادات", "expense": "مصروفات"}[x]
            )
        
        with col2:
            categories = ["الكل"] + list(set([t['category'] for t in st.session_state.transactions]))
            filter_category = st.selectbox("الفئة", categories)
        
        with col3:
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 مسح"):
                st.rerun()
        
        # تطبيق الفلاتر
        filtered = st.session_state.transactions.copy()
        
        if filter_type != "all":
            filtered = [t for t in filtered if t['type'] == filter_type]
        
        if filter_category != "الكل":
            filtered = [t for t in filtered if t['category'] == filter_category]
        
        # عرض الجدول
        if filtered:
            df = pd.DataFrame(filtered)
            df['النوع'] = df['type'].map({'revenue': 'إيراد', 'expense': 'مصروف'})
            df['التاريخ'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df['المبلغ'] = df['amount'].apply(lambda x: f"{x:,.2f} ج.م")
            
            display_df = df[['التاريخ', 'النوع', 'category', 'المبلغ', 'description']].copy()
            display_df.columns = ['التاريخ', 'النوع', 'الفئة', 'المبلغ', 'الوصف']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # خيار الحذف
            st.markdown("---")
            st.subheader("🗑️ حذف معاملة")
            
            trans_to_delete = st.selectbox(
                "اختر المعاملة للحذف:",
                options=filtered,
                format_func=lambda t: f"{t['date']} - {t['category']} - {t['amount']} ج.م"
            )
            
            if st.button("حذف المعاملة", type="primary"):
                delete_transaction(trans_to_delete['id'])
                st.success("✅ تم حذف المعاملة بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد معاملات تطابق الفلتر المحدد")
    else:
        st.info("📭 لا توجد معاملات حتى الآن")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: التقارير
with tab3:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    if st.session_state.transactions:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            date_from = st.date_input("من تاريخ:", value=datetime.now() - timedelta(days=30))
        
        with col2:
            date_to = st.date_input("إلى تاريخ:", value=datetime.now())
        
        with col3:
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            generate_btn = st.button("📊 إنشاء", type="primary")
        
        if generate_btn:
            df = pd.DataFrame(st.session_state.transactions)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            filtered = df[(df['date'] >= date_from) & (df['date'] <= date_to)]
            
            if not filtered.empty:
                revenues = filtered[filtered['type'] == 'revenue']
                expenses = filtered[filtered['type'] == 'expense']
                
                total_revenue = revenues['amount'].sum()
                total_expense = expenses['amount'].sum()
                net_profit = total_revenue - total_expense
                
                st.markdown("### 📊 ملخص التقرير")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("إجمالي الإيرادات", f"{total_revenue:,.2f} ج.م")
                
                with col2:
                    st.metric("إجمالي المصروفات", f"{total_expense:,.2f} ج.م")
                
                with col3:
                    st.metric("صافي الربح", f"{net_profit:,.2f} ج.م")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = filtered.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 تحميل CSV",
                        data=csv,
                        file_name=f"report_{date_from}_{date_to}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    json_data = filtered.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        label="📥 تحميل JSON",
                        data=json_data,
                        file_name=f"report_{date_from}_{date_to}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ لا توجد معاملات في هذه الفترة")
    else:
        st.info("📭 لا توجد معاملات لإنشاء التقرير")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: إضافة معاملة
with tab4:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    with st.form("add_transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_type = st.selectbox(
                "نوع المعاملة *",
                ["revenue", "expense"],
                format_func=lambda x: "إيراد" if x == "revenue" else "مصروف"
            )
            
            amount = st.number_input(
                "المبلغ (جنيه) *",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            category = st.selectbox(
                "الفئة *",
                ["مبيعات", "خدمات", "رواتب", "إيجار", "مواد خام", "تسويق", "مرافق", "صيانة", "أخرى"]
            )
            
            date = st.date_input("التاريخ *", value=datetime.now())
        
        description = st.text_area("الوصف", height=100)
        
        submitted = st.form_submit_button("💾 حفظ المعاملة", type="primary", use_container_width=True)
        
        if submitted:
            if amount > 0:
                add_transaction(trans_type, category, amount, date, description)
                st.success("✅ تم إضافة المعاملة بنجاح!")
                st.balloons()
            else:
                st.error("⚠️ يرجى إدخال مبلغ أكبر من صفر")
    
    st.markdown('</div>', unsafe_allow_html=True)
