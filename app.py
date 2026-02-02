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
    st.warning("⚠️ Plotly غير مثبت. سيتم استخدام الرسوم البيانية الأساسية من Streamlit.")

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة الأرباح والخسائر",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص للتصميم الاحترافي
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .profit {
        color: #27ae60;
        font-weight: bold;
        font-size: 24px;
    }
    
    .loss {
        color: #e74c3c;
        font-weight: bold;
        font-size: 24px;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
    }
    
    h1, h2, h3 {
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة البيانات في Session State
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

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

# العنوان الرئيسي
st.title("💰 نظام إدارة الأرباح والخسائر الاحترافي")
st.markdown("---")

# الشريط الجانبي - القائمة
with st.sidebar:
    st.header("📋 القائمة")
    page = st.radio(
        "اختر الصفحة:",
        ["🏠 لوحة التحكم", "➕ إضافة معاملة", "📊 المعاملات", "📈 التقارير"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # فلتر الفترة الزمنية
    if page == "🏠 لوحة التحكم":
        st.subheader("🕐 الفترة الزمنية")
        period = st.selectbox(
            "اختر الفترة:",
            ["all", "month", "week", "today"],
            format_func=lambda x: {
                "all": "الكل",
                "month": "هذا الشهر",
                "week": "هذا الأسبوع",
                "today": "اليوم"
            }[x]
        )
    else:
        period = "all"

# صفحة لوحة التحكم
if page == "🏠 لوحة التحكم":
    st.header("📊 لوحة التحكم")
    
    # الحصول على المعاملات المفلترة
    filtered_trans = get_filtered_transactions(period)
    total_revenue, total_expense, net_profit, profit_margin = calculate_stats(filtered_trans)
    
    # عرض الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 إجمالي الإيرادات",
            value=f"{total_revenue:,.2f} ج.م",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 إجمالي المصروفات",
            value=f"{total_expense:,.2f} ج.م",
            delta=None
        )
    
    with col3:
        profit_delta = "ربح" if net_profit >= 0 else "خسارة"
        st.metric(
            label="💰 صافي الربح/الخسارة",
            value=f"{net_profit:,.2f} ج.م",
            delta=profit_delta,
            delta_color="normal" if net_profit >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            label="📊 نسبة الربح",
            value=f"{profit_margin:.2f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # الرسوم البيانية
    if filtered_trans:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 الإيرادات vs المصروفات (آخر 7 أيام)")
            
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
            
            if PLOTLY_AVAILABLE:
                # رسم بياني خطي
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[d.strftime('%a') for d in dates],
                    y=revenue_data,
                    name='الإيرادات',
                    line=dict(color='#27ae60', width=3),
                    fill='tozeroy'
                ))
                fig.add_trace(go.Scatter(
                    x=[d.strftime('%a') for d in dates],
                    y=expense_data,
                    name='المصروفات',
                    line=dict(color='#e74c3c', width=3),
                    fill='tozeroy'
                ))
                fig.update_layout(
                    height=400,
                    showlegend=True,
                    hovermode='x unified',
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback: استخدام Streamlit line chart
                chart_df = pd.DataFrame({
                    'التاريخ': [d.strftime('%a') for d in dates],
                    'الإيرادات': revenue_data,
                    'المصروفات': expense_data
                })
                st.line_chart(chart_df.set_index('التاريخ'))
        
        with col2:
            st.subheader("🥧 توزيع الإيرادات والمصروفات")
            
            if PLOTLY_AVAILABLE:
                # رسم دائري
                fig = go.Figure(data=[go.Pie(
                    labels=['الإيرادات', 'المصروفات'],
                    values=[total_revenue, total_expense],
                    marker=dict(colors=['#27ae60', '#e74c3c']),
                    hole=0.4
                )])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback: عرض بسيط بالأرقام
                st.metric("الإيرادات", f"{total_revenue:,.2f} ج.م")
                st.metric("المصروفات", f"{total_expense:,.2f} ج.م")
                if total_revenue + total_expense > 0:
                    st.progress(total_revenue / (total_revenue + total_expense))
                    st.caption(f"نسبة الإيرادات: {total_revenue/(total_revenue + total_expense)*100:.1f}%")
        
        # رسم بياني شهري
        st.subheader("📊 المقارنة الشهرية")
        
        if st.session_state.transactions:
            df = pd.DataFrame(st.session_state.transactions)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M').astype(str)
            
            monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
            
            if not monthly.empty:
                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    if 'revenue' in monthly.columns:
                        fig.add_trace(go.Bar(
                            x=monthly.index,
                            y=monthly['revenue'],
                            name='الإيرادات',
                            marker_color='#27ae60'
                        ))
                    if 'expense' in monthly.columns:
                        fig.add_trace(go.Bar(
                            x=monthly.index,
                            y=monthly['expense'],
                            name='المصروفات',
                            marker_color='#e74c3c'
                        ))
                    fig.update_layout(
                        height=400,
                        barmode='group',
                        showlegend=True,
                        plot_bgcolor='white'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback: استخدام Streamlit bar chart
                    st.bar_chart(monthly)
    else:
        st.info("📭 لا توجد معاملات في هذه الفترة. ابدأ بإضافة معاملاتك!")

# صفحة إضافة معاملة
elif page == "➕ إضافة معاملة":
    st.header("➕ إضافة معاملة جديدة")
    
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
            
            date = st.date_input(
                "التاريخ *",
                value=datetime.now()
            )
        
        description = st.text_area("الوصف", height=100)
        
        submitted = st.form_submit_button("💾 حفظ المعاملة")
        
        if submitted:
            if amount > 0:
                add_transaction(trans_type, category, amount, date, description)
                st.success("✅ تم إضافة المعاملة بنجاح!")
                st.balloons()
            else:
                st.error("⚠️ يرجى إدخال مبلغ أكبر من صفر")

# صفحة المعاملات
elif page == "📊 المعاملات":
    st.header("📊 جميع المعاملات")
    
    if st.session_state.transactions:
        # فلاتر
        col1, col2, col3 = st.columns(3)
        
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
            if st.button("🔄 مسح الفلاتر"):
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
                hide_index=True
            )
            
            # خيار الحذف
            st.markdown("---")
            st.subheader("🗑️ حذف معاملة")
            
            trans_to_delete = st.selectbox(
                "اختر المعاملة للحذف:",
                options=filtered,
                format_func=lambda t: f"{t['date']} - {t['category']} - {t['amount']} ج.م"
            )
            
            if st.button("🗑️ حذف المعاملة المحددة", type="secondary"):
                delete_transaction(trans_to_delete['id'])
                st.success("✅ تم حذف المعاملة بنجاح!")
                st.rerun()
        else:
            st.info("لا توجد معاملات تطابق الفلتر المحدد")
    else:
        st.info("📭 لا توجد معاملات حتى الآن. ابدأ بإضافة معاملاتك!")

# صفحة التقارير
elif page == "📈 التقارير":
    st.header("📈 التقارير المفصلة")
    
    if st.session_state.transactions:
        # اختيار الفترة
        col1, col2 = st.columns(2)
        
        with col1:
            date_from = st.date_input("من تاريخ:", value=datetime.now() - timedelta(days=30))
        
        with col2:
            date_to = st.date_input("إلى تاريخ:", value=datetime.now())
        
        if st.button("📊 إنشاء التقرير"):
            # فلترة حسب التاريخ
            df = pd.DataFrame(st.session_state.transactions)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            filtered = df[(df['date'] >= date_from) & (df['date'] <= date_to)]
            
            if not filtered.empty:
                revenues = filtered[filtered['type'] == 'revenue']
                expenses = filtered[filtered['type'] == 'expense']
                
                total_revenue = revenues['amount'].sum()
                total_expense = expenses['amount'].sum()
                net_profit = total_revenue - total_expense
                
                # عرض الإحصائيات
                st.markdown("### 📊 ملخص التقرير")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("إجمالي الإيرادات", f"{total_revenue:,.2f} ج.م")
                
                with col2:
                    st.metric("إجمالي المصروفات", f"{total_expense:,.2f} ج.م")
                
                with col3:
                    st.metric(
                        "صافي الربح",
                        f"{net_profit:,.2f} ج.م",
                        delta="ربح" if net_profit >= 0 else "خسارة"
                    )
                
                st.markdown("---")
                
                # التفاصيل حسب الفئة
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📈 الإيرادات حسب الفئة")
                    if not revenues.empty:
                        revenue_by_cat = revenues.groupby('category')['amount'].sum().sort_values(ascending=False)
                        for cat, amount in revenue_by_cat.items():
                            st.write(f"**{cat}:** {amount:,.2f} ج.م")
                
                with col2:
                    st.markdown("### 📉 المصروفات حسب الفئة")
                    if not expenses.empty:
                        expense_by_cat = expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
                        for cat, amount in expense_by_cat.items():
                            st.write(f"**{cat}:** {amount:,.2f} ج.م")
                
                # تصدير البيانات
                st.markdown("---")
                st.markdown("### 📥 تصدير البيانات")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = filtered.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 تحميل CSV",
                        data=csv,
                        file_name=f"report_{date_from}_{date_to}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json_data = filtered.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        label="📥 تحميل JSON",
                        data=json_data,
                        file_name=f"report_{date_from}_{date_to}.json",
                        mime="application/json"
                    )
            else:
                st.warning("⚠️ لا توجد معاملات في هذه الفترة")
    else:
        st.info("📭 لا توجد معاملات لإنشاء التقرير")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>💰 نظام إدارة الأرباح والخسائر | تم التطوير بواسطة Streamlit</div>",
    unsafe_allow_html=True
)
