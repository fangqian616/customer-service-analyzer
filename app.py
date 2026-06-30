#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海尔京东客服舆情分析系统 - Streamlit Web应用
"""

import streamlit as st
import sys
import os
import json
import tempfile
import time
from datetime import datetime

# 确保模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_log_file, get_summary_stats, KEYWORD_CATEGORIES, NEGATIVE_WORDS, POSITIVE_WORDS
from visualizer import generate_pdf_report

# ── i18n 翻译字典 ──
LANG = {
    "zh": {
        # Page
        "page_title": "客服舆情分析系统",
        "main_title": "📊 客服聊天记录舆情分析系统",
        "main_desc": "上传飞书导出的聊天记录文件，自动完成数据解析、关键词提取、可视化分析，一键导出PDF报告。",
        # Sidebar
        "sidebar_title": "客服舆情分析",
        "sidebar_caption": "上传聊天记录，一键生成分析报告",
        "ai_analysis": "AI分析（可选）",
        "api_key_label": "DeepSeek API Key",
        "api_key_help": "填入后可生成AI深度分析文本，留空则仅生成数据报告",
        "api_base_label": "API Base URL",
        "api_base_help": "默认使用DeepSeek官方，也可替换为兼容接口",
        "parse_params": "解析参数",
        "max_conv_label": "最大解析会话数",
        "max_conv_help": "限制解析数量以加快速度",
        "file_encoding": "文件编码",
        "ai_prompt_config": "AI提示词配置",
        "analysis_rounds_label": "分析轮次",
        "analysis_rounds_help": "每轮AI会基于上一轮结论深化分析，轮次越多越深入但耗时越长",
        "analysis_modules": "**分析模块**",
        "module_label": "模块{}",
        "del_module_help": "删除此模块",
        "new_module_name": "新增模块名称",
        "new_module_placeholder": "输入后按回车添加",
        "extra_instructions": "额外指令",
        "extra_instructions_placeholder": "如：重点关注冰箱品类、需对比上月数据、强调售后流程问题...",
        "extra_instructions_help": "追加到提示词末尾的额外要求，会指导AI的分析方向",
        "restore_defaults": "恢复默认模块",
        # Upload
        "upload_label": "上传聊天记录文件",
        "upload_help": "支持飞书导出的聊天记录格式（.log / .txt）",
        # Parsing
        "parsing": "正在解析聊天记录...",
        "parse_success": "解析完成！耗时 {:.1f}s，共 {:,} 条会话",
        "parse_error": "解析失败：{}",
        # Metrics
        "total_conversations": "会话总数",
        "customer_messages": "客户消息",
        "agent_messages": "客服消息",
        "num_agents": "客服人数",
        "date_range": "数据周期",
        # Tabs
        "tab_daily": "📈 每日趋势",
        "tab_keywords": "🔑 关键词分析",
        "tab_negative": "⚠️ 负面深度",
        "tab_scenarios": "📋 场景排名",
        "tab_export": "📥 导出报告",
        # Tab1
        "daily_trend_title": "每日会话与消息趋势",
        "daily_conv_title": "每日会话量",
        "conv_count_ylabel": "会话数",
        "customer_vs_agent_title": "客户 vs 客服消息量",
        "customer_label": "客户",
        "agent_label": "客服",
        "peak_day_conv": "峰值日会话",
        "avg_daily_conv": "日均会话",
        "agent_customer_ratio": "客服/客户比",
        # Tab2
        "kw_freq_sentiment_title": "关键词频次与情感分析",
        "kw_top15_title": "关键词 TOP15",
        "sentiment_title": "情感分类",
        "neutral_label": "中性",
        "negative_label": "负面",
        "positive_label": "正面",
        "kw_freq_table_title": "关键词频次表",
        "kw_col": "关键词",
        "freq_col": "频次",
        "sentiment_col": "情感",
        # Tab3
        "neg_depth_title": "负面情绪深度分析",
        "neg_kw_rank_title": "负面关键词排行",
        "neg_category_title": "负面问题分类归集",
        "cat_after_sales": "售后流程",
        "cat_product_quality": "产品质量",
        "cat_usage_issue": "使用异常",
        "cat_emotional": "情绪表达",
        "neg_sample_title": "负面对话样本",
        "sample_label": "样本 {}",
        # Tab4
        "scenario_rank_title": "用户咨询场景分类排名",
        "scenario_chart_title": "咨询场景排名（从高到低）",
        "scenario_pie_title": "场景占比分布",
        "scenario_detail_title": "场景详情",
        "total_times": "合计",
        "times_unit": "次",
        # Tab5
        "export_pdf_title": "导出PDF报告",
        "data_viz_report": "#### 📊 数据可视化报告",
        "data_viz_desc": "包含7页图表：封面、每日趋势、关键词分析、负面深度、场景排名、场景拆解、售前售后对比",
        "gen_data_report": "生成数据报告",
        "generating_pdf": "正在生成PDF...",
        "download_data_report": "📥 下载数据报告",
        "data_report_filename": "客服舆情分析_数据报告_{}.pdf",
        "gen_failed": "生成失败: {}",
        "full_report": "#### 📊+📝 完整分析报告",
        "full_report_desc": "数据图表 + AI深度分析文本（需要DeepSeek API Key）",
        "api_key_warning": "请先在侧边栏填入DeepSeek API Key",
        "gen_full_report": "生成完整报告",
        "calling_ai": "正在调用AI分析...",
        "download_full_report": "📥 下载完整报告",
        "full_report_filename": "客服舆情分析_完整报告_{}.pdf",
        # Guide
        "guide_title": "### 📤 使用说明",
        "guide_step1": "1. 将飞书导出的聊天记录文件（.log / .txt）拖到上方上传区",
        "guide_step2": "2. 系统自动解析数据并展示交互式图表",
        "guide_step3": "3. 切换到「导出报告」Tab，一键生成PDF报告",
        "guide_format": "**支持的格式：** 飞书导出的客服聊天记录",
        "guide_features": "**功能：**\n- 每日会话趋势分析\n- 关键词频次统计与情感分类\n- 负面情绪深度分析与对话样本\n- 13类咨询场景自动分类排名\n- 售前/售后对比分析\n- 可选接入DeepSeek AI生成深度分析文本",
        # Default modules
        "default_modules": [
            "整体舆情态势",
            "核心痛点TOP5（每个痛点配3条典型原话）",
            "产品质量问题汇总",
            "服务体验问题",
            "国补/促销政策相关舆情",
            "情感分布判断",
            "风险预警",
            "改进建议",
        ],
    },
    "en": {
        # Page
        "page_title": "Customer Service Sentiment Analyzer",
        "main_title": "📊 Customer Service Chat Sentiment Analysis",
        "main_desc": "Upload Feishu chat logs for automatic parsing, keyword extraction, visual analysis, and one-click PDF export.",
        # Sidebar
        "sidebar_title": "Sentiment Analysis",
        "sidebar_caption": "Upload chat logs, generate reports with one click",
        "ai_analysis": "AI Analysis (Optional)",
        "api_key_label": "DeepSeek API Key",
        "api_key_help": "Enter to enable AI deep analysis; leave empty for data reports only",
        "api_base_label": "API Base URL",
        "api_base_help": "Default: DeepSeek official; replace with compatible endpoint if needed",
        "parse_params": "Parse Parameters",
        "max_conv_label": "Max Conversations",
        "max_conv_help": "Limit parsing count to speed up processing",
        "file_encoding": "File Encoding",
        "ai_prompt_config": "AI Prompt Config",
        "analysis_rounds_label": "Analysis Rounds",
        "analysis_rounds_help": "Each round deepens analysis based on previous conclusions; more rounds = deeper but slower",
        "analysis_modules": "**Analysis Modules**",
        "module_label": "Module {}",
        "del_module_help": "Delete this module",
        "new_module_name": "New Module Name",
        "new_module_placeholder": "Type and press Enter to add",
        "extra_instructions": "Extra Instructions",
        "extra_instructions_placeholder": "e.g. Focus on refrigerator category, compare with last month, emphasize after-sales issues...",
        "extra_instructions_help": "Appended to the prompt to guide AI analysis direction",
        "restore_defaults": "Restore Defaults",
        # Upload
        "upload_label": "Upload Chat Log File",
        "upload_help": "Supports Feishu exported chat log formats (.log / .txt)",
        # Parsing
        "parsing": "Parsing chat logs...",
        "parse_success": "Parsing complete! {:.1f}s, {:,} conversations",
        "parse_error": "Parse failed: {}",
        # Metrics
        "total_conversations": "Total Conversations",
        "customer_messages": "Customer Messages",
        "agent_messages": "Agent Messages",
        "num_agents": "Agent Count",
        "date_range": "Date Range",
        # Tabs
        "tab_daily": "📈 Daily Trends",
        "tab_keywords": "🔑 Keyword Analysis",
        "tab_negative": "⚠️ Negative Insights",
        "tab_scenarios": "📋 Scenario Ranking",
        "tab_export": "📥 Export Reports",
        # Tab1
        "daily_trend_title": "Daily Conversation & Message Trends",
        "daily_conv_title": "Daily Conversations",
        "conv_count_ylabel": "Conversations",
        "customer_vs_agent_title": "Customer vs Agent Messages",
        "customer_label": "Customer",
        "agent_label": "Agent",
        "peak_day_conv": "Peak Day Conv.",
        "avg_daily_conv": "Avg. Daily Conv.",
        "agent_customer_ratio": "Agent/Customer Ratio",
        # Tab2
        "kw_freq_sentiment_title": "Keyword Frequency & Sentiment Analysis",
        "kw_top15_title": "Keywords TOP15",
        "sentiment_title": "Sentiment Distribution",
        "neutral_label": "Neutral",
        "negative_label": "Negative",
        "positive_label": "Positive",
        "kw_freq_table_title": "Keyword Frequency Table",
        "kw_col": "Keyword",
        "freq_col": "Frequency",
        "sentiment_col": "Sentiment",
        # Tab3
        "neg_depth_title": "Negative Sentiment Deep Analysis",
        "neg_kw_rank_title": "Negative Keyword Ranking",
        "neg_category_title": "Negative Issue Classification",
        "cat_after_sales": "After-sales Process",
        "cat_product_quality": "Product Quality",
        "cat_usage_issue": "Usage Issues",
        "cat_emotional": "Emotional Expression",
        "neg_sample_title": "Negative Conversation Samples",
        "sample_label": "Sample {}",
        # Tab4
        "scenario_rank_title": "User Inquiry Scenario Ranking",
        "scenario_chart_title": "Scenario Ranking (High to Low)",
        "scenario_pie_title": "Scenario Distribution",
        "scenario_detail_title": "Scenario Details",
        "total_times": "Total",
        "times_unit": "times",
        # Tab5
        "export_pdf_title": "Export PDF Report",
        "data_viz_report": "#### 📊 Data Visualization Report",
        "data_viz_desc": "7-page charts: Cover, Daily Trends, Keywords, Negative Insights, Scenarios, Scenario Breakdown, Pre/Post-sales Comparison",
        "gen_data_report": "Generate Data Report",
        "generating_pdf": "Generating PDF...",
        "download_data_report": "📥 Download Data Report",
        "data_report_filename": "SentimentAnalysis_DataReport_{}.pdf",
        "gen_failed": "Generation failed: {}",
        "full_report": "#### 📊+📝 Full Analysis Report",
        "full_report_desc": "Data charts + AI deep analysis text (DeepSeek API Key required)",
        "api_key_warning": "Please enter DeepSeek API Key in the sidebar first",
        "gen_full_report": "Generate Full Report",
        "calling_ai": "Calling AI analysis...",
        "download_full_report": "📥 Download Full Report",
        "full_report_filename": "SentimentAnalysis_FullReport_{}.pdf",
        # Guide
        "guide_title": "### 📤 Instructions",
        "guide_step1": "1. Drag and drop your Feishu chat log file (.log / .txt) to the upload area above",
        "guide_step2": "2. The system will automatically parse data and display interactive charts",
        "guide_step3": '3. Switch to the "Export Reports" tab to generate a PDF report with one click',
        "guide_format": "**Supported formats:** Feishu exported customer service chat logs",
        "guide_features": "**Features:**\n- Daily conversation trend analysis\n- Keyword frequency statistics and sentiment classification\n- Negative sentiment deep analysis with conversation samples\n- 13 categories of inquiry scenario auto-classification\n- Pre-sales / post-sales comparison analysis\n- Optional DeepSeek AI integration for deep analysis text",
        # Default modules
        "default_modules": [
            "Overall Sentiment Overview",
            "Top 5 Core Pain Points (with 3 typical quotes each)",
            "Product Quality Issues Summary",
            "Service Experience Issues",
            "National Subsidy / Promotion Related Sentiment",
            "Sentiment Distribution Assessment",
            "Risk Warnings",
            "Improvement Recommendations",
        ],
    }
}


def t(key, *args):
    lang = st.session_state.get("lang", "zh")
    text = LANG.get(lang, LANG["zh"]).get(key, key)
    if args:
        text = text.format(*args)
    return text


# ── 页面配置 ──
st.set_page_config(
    page_title=t("page_title"),
    page_icon="📊",
    layout="wide",
)

# ── 自定义CSS ──
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #2C3E50; }
    .metric-card { 
        background: white; border-radius: 10px; padding: 20px; 
        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .metric-value { font-size: 2rem; font-weight: 700; }
    .metric-label { font-size: 0.9rem; color: #7F8C8D; }
    .stProgress > div > div { background-color: #4C72B0; }
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ──
with st.sidebar:
    # 语言切换
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇨🇳 中文", use_container_width=True, disabled=st.session_state.get("lang","zh")=="zh"):
            st.session_state["lang"] = "zh"
            st.rerun()
    with lang_col2:
        if st.button("🇬🇧 EN", use_container_width=True, disabled=st.session_state.get("lang","zh")=="en"):
            st.session_state["lang"] = "en"
            st.rerun()
    st.divider()

    st.image("https://img.icons8.com/fluency/96/chat.png", width=60)
    st.title(t("sidebar_title"))
    st.caption(t("sidebar_caption"))
    
    st.divider()
    
    # DeepSeek API（可选）
    st.subheader(t("ai_analysis"))
    deepseek_key = st.text_input(t("api_key_label"), type="password", 
                                  help=t("api_key_help"))
    deepseek_base = st.text_input(t("api_base_label"), value="https://api.deepseek.com/v1",
                                   help=t("api_base_help"))
    
    st.divider()
    
    # 解析参数
    st.subheader(t("parse_params"))
    max_conv = st.number_input(t("max_conv_label"), min_value=100, max_value=100000, 
                                value=20000, step=5000, help=t("max_conv_help"))
    encoding = st.selectbox(t("file_encoding"), ["utf-8", "gbk", "gb2312", "utf-16"], index=0)
    
    st.divider()
    
    # ── AI提示词自定义 ──
    st.subheader(t("ai_prompt_config"))
    
    # 分析轮次
    analysis_rounds = st.number_input(t("analysis_rounds_label"), min_value=1, max_value=10,
                                       value=st.session_state.get('analysis_rounds', 1), step=1,
                                       help=t("analysis_rounds_help"))
    st.session_state['analysis_rounds'] = analysis_rounds
    
    # 分析模块管理
    st.markdown(t("analysis_modules"))
    
    if 'custom_modules' not in st.session_state:
        st.session_state['custom_modules'] = LANG.get(st.session_state.get("lang", "zh"), LANG["zh"])["default_modules"].copy()
    
    # 显示并编辑现有模块
    modules_to_remove = []
    for i, mod in enumerate(st.session_state['custom_modules']):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            new_val = st.text_input(t("module_label", i+1), value=mod, key=f"mod_{i}", label_visibility="collapsed")
            if new_val != mod:
                st.session_state['custom_modules'][i] = new_val
        with col_b:
            if st.button("🗑", key=f"del_mod_{i}", help=t("del_module_help")):
                modules_to_remove.append(i)
    # 删除标记的模块
    for idx in reversed(modules_to_remove):
        st.session_state['custom_modules'].pop(idx)
        st.rerun()
    
    # 新增模块
    new_module = st.text_input(t("new_module_name"), key="new_module_input", placeholder=t("new_module_placeholder"))
    if new_module and new_module not in st.session_state['custom_modules']:
        st.session_state['custom_modules'].append(new_module)
        st.rerun()
    
    # 额外指令
    extra_instructions = st.text_area(t("extra_instructions"), value=st.session_state.get('extra_instructions', ''), height=80,
                                       placeholder=t("extra_instructions_placeholder"),
                                       help=t("extra_instructions_help"))
    st.session_state['extra_instructions'] = extra_instructions
    
    # 恢复默认
    if st.button(t("restore_defaults")):
        st.session_state['custom_modules'] = LANG.get(st.session_state.get("lang", "zh"), LANG["zh"])["default_modules"].copy()
        st.rerun()

# ── 主区域 ──
st.markdown(f'<p class="main-title">{t("main_title")}</p>', unsafe_allow_html=True)
st.markdown(t("main_desc"))

# ── 文件上传 ──
uploaded_file = st.file_uploader(
    t("upload_label"),
    type=["log", "txt", "csv"],
    help=t("upload_help")
)

if uploaded_file is not None:
    # 保存上传文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    # ── 解析数据 ──
    with st.spinner(t("parsing")):
        t0 = time.time()
        try:
            parsed = parse_log_file(tmp_path, encoding=encoding, max_conversations=max_conv)
            summary = get_summary_stats(parsed)
            parse_time = time.time() - t0
            st.success(t("parse_success", parse_time, summary['total_conversations']))
        except Exception as e:
            st.error(t("parse_error", e))
            st.stop()
    
    # ── 概览指标 ──
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(t("total_conversations"), f"{summary['total_conversations']:,}")
    with col2:
        st.metric(t("customer_messages"), f"{summary['total_customer_msgs']:,}")
    with col3:
        st.metric(t("agent_messages"), f"{summary['total_agent_msgs']:,}")
    with col4:
        st.metric(t("num_agents"), str(summary['num_agents']))
    with col5:
        st.metric(t("date_range"), summary['date_range'])
    
    # ── Tab区域 ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t("tab_daily"), t("tab_keywords"), t("tab_negative"), 
        t("tab_scenarios"), t("tab_export")
    ])
    
    # ═══ Tab1: 每日趋势 ═══
    with tab1:
        st.subheader(t("daily_trend_title"))
        
        daily = parsed['daily_stats']
        dates = list(daily.keys())
        
        if dates:
            import matplotlib.pyplot as plt
            import numpy as np
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            short_dates = [d[5:] for d in dates]
            conv_vals = [daily[d]['conv'] for d in dates]
            cust_vals = [daily[d]['customer'] for d in dates]
            agent_vals = [daily[d]['agent'] for d in dates]
            
            ax1.bar(short_dates, conv_vals, color='#4C72B0', alpha=0.85)
            ax1.set_title(t("daily_conv_title"), fontsize=13)
            ax1.set_ylabel(t("conv_count_ylabel"))
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(axis='y', alpha=0.3)
            
            x_pos = np.arange(len(dates))
            ax2.bar(x_pos - 0.19, cust_vals, 0.38, color='#DD8452', alpha=0.85, label=t("customer_label"))
            ax2.bar(x_pos + 0.19, agent_vals, 0.38, color='#55A868', alpha=0.85, label=t("agent_label"))
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(short_dates, fontsize=8)
            ax2.set_title(t("customer_vs_agent_title"), fontsize=13)
            ax2.legend()
            ax2.grid(axis='y', alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 日均统计
            col1, col2, col3 = st.columns(3)
            if conv_vals:
                col1.metric(t("peak_day_conv"), f"{max(conv_vals):,}", f"{dates[conv_vals.index(max(conv_vals))]}")
                col2.metric(t("avg_daily_conv"), f"{np.mean(conv_vals):.0f}")
                col3.metric(t("agent_customer_ratio"), f"{np.mean(agent_vals)/max(np.mean(cust_vals),1):.1f}")
    
    # ═══ Tab2: 关键词分析 ═══
    with tab2:
        st.subheader(t("kw_freq_sentiment_title"))
        
        kw = parsed['keyword_counts']
        if kw:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
            
            top15 = kw.most_common(15)
            top15.reverse()
            names = [k for k, v in top15]
            vals = [v for k, v in top15]
            colors = []
            for k in names:
                if k in NEGATIVE_WORDS: colors.append('#C44E52')
                elif k in POSITIVE_WORDS: colors.append('#55A868')
                else: colors.append('#4C72B0')
            
            ax1.barh(names, vals, color=colors, alpha=0.85, height=0.65)
            ax1.set_title(t("kw_top15_title"), fontsize=13)
            for i, v in enumerate(vals):
                ax1.text(v + max(vals)*0.01, i, str(v), va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 情感饼图
            pos_t = sum(v for k, v in kw.items() if k in POSITIVE_WORDS)
            neg_t = sum(v for k, v in kw.items() if k in NEGATIVE_WORDS)
            neu_t = sum(kw.values()) - pos_t - neg_t
            ax2.pie([neu_t, neg_t, pos_t], 
                    labels=[f'{t("neutral_label")} {neu_t}', f'{t("negative_label")} {neg_t}', f'{t("positive_label")} {pos_t}'],
                    colors=['#4C72B0', '#C44E52', '#55A868'],
                    autopct='%1.1f%%', startangle=140)
            ax2.set_title(t("sentiment_title"), fontsize=13)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 关键词表格
            st.subheader(t("kw_freq_table_title"))
            kw_df_data = [{t("kw_col"): k, t("freq_col"): v, t("sentiment_col"): t("negative_label") if k in NEGATIVE_WORDS else (t("positive_label") if k in POSITIVE_WORDS else t("neutral_label"))} 
                          for k, v in kw.most_common(30)]
            st.dataframe(kw_df_data, use_container_width=True, hide_index=True)
    
    # ═══ Tab3: 负面深度 ═══
    with tab3:
        st.subheader(t("neg_depth_title"))
        
        neg_kw = {k: v for k, v in kw.items() if k in NEGATIVE_WORDS}
        if neg_kw:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
            
            neg_sorted = sorted(neg_kw.items(), key=lambda x: x[1], reverse=True)
            n_names = [k for k, v in neg_sorted]
            n_vals = [v for k, v in neg_sorted]
            red_grad = plt.cm.Reds(np.linspace(0.35, 0.85, len(n_names)))
            ax1.barh(n_names[::-1], n_vals[::-1], color=red_grad, height=0.65, alpha=0.9)
            ax1.set_title(t("neg_kw_rank_title"), fontsize=13)
            for i, v in enumerate(n_vals[::-1]):
                ax1.text(v + 1, i, str(v), va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 问题分类
            from collections import OrderedDict
            cat_defs = [
                ("cat_after_sales", ["退货", "退款", "换货", "投诉", "赔偿"]),
                ("cat_product_quality", ["质量", "制冷", "不制冷", "故障", "损坏"]),
                ("cat_usage_issue", ["噪音", "结冰", "漏水", "异响"]),
                ("cat_emotional", ["不满", "坑", "差评", "失望", "假货", "骗"]),
            ]
            cats = OrderedDict()
            for cat_key, kws in cat_defs:
                cats[t(cat_key)] = sum(neg_kw.get(k, 0) for k in kws)
            cat_colors = ['#C44E52', '#DD8452', '#CCA64C', '#8172B3']
            bars = ax2.bar(list(cats.keys()), list(cats.values()), color=cat_colors, alpha=0.85, width=0.55)
            for bar, val in zip(bars, cats.values()):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val),
                        ha='center', fontsize=11, fontweight='bold')
            ax2.set_title(t("neg_category_title"), fontsize=13)
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 负面对话样本
            st.subheader(t("neg_sample_title"))
            sample = parsed['sample_negative'][:10]
            for i, conv in enumerate(sample):
                customer_msgs = [m['content'] for m in conv if m['role'] == 'customer']
                if customer_msgs:
                    with st.expander(t("sample_label", i+1)):
                        for msg in customer_msgs[:5]:
                            st.markdown(f"👤 {msg}")
    
    # ═══ Tab4: 场景排名 ═══
    with tab4:
        st.subheader(t("scenario_rank_title"))
        
        scenarios = OrderedDict()
        for cat, kws_list in KEYWORD_CATEGORIES.items():
            detail = {kw: parsed['keyword_counts'].get(kw, 0) for kw in kws_list if parsed['keyword_counts'].get(kw, 0) > 0}
            if detail:
                scenarios[cat] = detail
        
        scenario_sorted = sorted(scenarios.items(), key=lambda x: sum(x[1].values()), reverse=True)
        s_names = [s[0] for s in scenario_sorted]
        s_totals = [sum(s[1].values()) for s in scenario_sorted]
        grand_total = sum(s_totals)
        
        if s_names:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            sc = []
            for name in s_names:
                if name in ["好评满意"]: sc.append('#55A868')
                elif name in ["售后退换", "产品质量", "维修保修", "投诉不满"]: sc.append('#C44E52')
                elif name in ["物流配送", "安装服务", "发票开票"]: sc.append('#DD8452')
                else: sc.append('#4C72B0')
            
            s_names_rev = s_names[::-1]
            s_totals_rev = s_totals[::-1]
            sc_rev = sc[::-1]
            ax1.barh(s_names_rev, s_totals_rev, color=sc_rev, alpha=0.85, height=0.65)
            ax1.set_title(t("scenario_chart_title"), fontsize=13)
            for i, v in enumerate(s_totals_rev):
                ax1.text(v + max(s_totals)*0.01, i, f'{v} ({v/grand_total*100:.1f}%)', va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 饼图
            top_n = min(6, len(s_names))
            pie_labels = s_names[:top_n] + ['其他' if st.session_state.get("lang","zh")=="zh" else "Other"]
            pie_vals = s_totals[:top_n] + [sum(s_totals[top_n:])]
            pie_c = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860', '#95A5A6']
            ax2.pie(pie_vals, labels=[f'{l}\n{v}' for l, v in zip(pie_labels, pie_vals)],
                    colors=pie_c[:len(pie_vals)], autopct='%1.1f%%', startangle=140)
            ax2.set_title(t("scenario_pie_title"), fontsize=13)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 场景详情表
            st.subheader(t("scenario_detail_title"))
            for name, detail in scenario_sorted:
                total = sum(detail.values())
                sub_str = "、".join(f"{k}({v})" for k, v in sorted(detail.items(), key=lambda x: x[1], reverse=True))
                st.markdown(f"**{name}** — {t('total_times')} {total} {t('times_unit')}  \n{sub_str}")
    
    # ═══ Tab5: 导出报告 ═══
    with tab5:
        st.subheader(t("export_pdf_title"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(t("data_viz_report"))
            st.markdown(t("data_viz_desc"))
            
            if st.button(t("gen_data_report"), key="gen_data"):
                with st.spinner(t("generating_pdf")):
                    try:
                        pdf_tmp = tempfile.mktemp(suffix='.pdf')
                        generate_pdf_report(parsed, pdf_tmp)
                        with open(pdf_tmp, 'rb') as f:
                            st.download_button(
                                label=t("download_data_report"),
                                data=f.read(),
                                file_name=t("data_report_filename", datetime.now().strftime('%Y%m%d')),
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(t("gen_failed", e))
        
        with col2:
            st.markdown(t("full_report"))
            st.markdown(t("full_report_desc"))
            
            if not deepseek_key:
                st.warning(t("api_key_warning"))
            
            if st.button(t("gen_full_report"), key="gen_full", disabled=not deepseek_key):
                with st.spinner(t("calling_ai")):
                    try:
                        # 调用DeepSeek API
                        ai_text = _call_deepseek(
                            deepseek_key, deepseek_base, parsed, summary,
                            custom_modules=st.session_state.get('custom_modules'),
                            analysis_rounds=st.session_state.get('analysis_rounds', 1),
                            extra_instructions=st.session_state.get('extra_instructions', '')
                        )
                        
                        pdf_tmp = tempfile.mktemp(suffix='.pdf')
                        generate_pdf_report(parsed, pdf_tmp, ai_report_text=ai_text)
                        
                        with open(pdf_tmp, 'rb') as f:
                            st.download_button(
                                label=t("download_full_report"),
                                data=f.read(),
                                file_name=t("full_report_filename", datetime.now().strftime('%Y%m%d')),
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(t("gen_failed", e))
    
    # 清理临时文件
    try:
        os.unlink(tmp_path)
    except:
        pass

else:
    # 没有上传文件时的引导
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"""
        {t("guide_title")}
        
        {t("guide_step1")}
        {t("guide_step2")}
        {t("guide_step3")}
        
        {t("guide_format")}
        
        {t("guide_features")}
        """)


def _call_deepseek(api_key, api_base, parsed_data, summary, custom_modules=None, analysis_rounds=1, extra_instructions=""):
    """调用DeepSeek API生成分析文本，支持自定义模块、多轮分析和额外指令"""
    import requests
    
    lang = st.session_state.get("lang", "zh")
    keyword_counts = parsed_data['keyword_counts']
    top_kw = keyword_counts.most_common(20)
    
    if lang == "zh":
        kw_str = "\n".join(f"  {k}: {v}次" for k, v in top_kw)
    else:
        kw_str = "\n".join(f"  {k}: {v} times" for k, v in top_kw)
    
    # 构建负面对话样本
    if lang == "zh":
        role_agent = "客服"
        role_customer = "客户"
        conv_label = "会话"
    else:
        role_agent = "Agent"
        role_customer = "Customer"
        conv_label = "Conversation"
    
    sample_str = ""
    for i, conv in enumerate(parsed_data['sample_negative'][:15]):
        sample_str += f"\n--- {conv_label}{i+1} ---\n"
        for msg in conv[:6]:
            role = role_agent if msg['role'] == 'agent' else role_customer
            sample_str += f"[{msg.get('date', '')}] {role}: {msg['content']}\n"
    
    # 构建模块列表
    if not custom_modules:
        custom_modules = LANG.get(lang, LANG["zh"])["default_modules"].copy()
    
    modules_text = "\n".join(f"### {i+1}. {mod}" for i, mod in enumerate(custom_modules))
    
    # 轮次说明
    round_instruction = ""
    if analysis_rounds > 1:
        if lang == "zh":
            round_instruction = f"\n\n【多轮分析要求】共需进行{analysis_rounds}轮分析。每轮在前一轮结论基础上深化，第1轮为初步分析，后续轮次需指出前轮的不足并补充新视角。最终输出合并所有轮次的综合结论。"
        else:
            round_instruction = f"\n\n[Multi-round Analysis] A total of {analysis_rounds} rounds are required. Each round deepens based on the previous round's conclusions. Round 1 is the initial analysis; subsequent rounds must identify gaps in previous rounds and add new perspectives. The final output combines conclusions from all rounds."
    
    # 额外指令
    extra_text = ""
    if extra_instructions.strip():
        if lang == "zh":
            extra_text = f"\n\n【额外要求】{extra_instructions.strip()}"
        else:
            extra_text = f"\n\n[Additional Requirements] {extra_instructions.strip()}"
    
    if lang == "zh":
        prompt = f"""你是数据分析专家，基于以下京东客服聊天记录数据生成舆情分析报告。直接输出报告正文，不要自我介绍，不要写"DeepSeek AI"。

数据概况:
  会话总数: {summary['total_conversations']}
  日期范围: {summary['date_range']}
  客户消息: {summary['total_customer_msgs']}
  客服消息: {summary['total_agent_msgs']}

关键词频次TOP20:
{kw_str}

负面对话样本:
{sample_str}

请输出{len(custom_modules)}个模块的分析：
{modules_text}
{round_instruction}{extra_text}"""
    else:
        prompt = f"""You are a data analysis expert. Generate a sentiment analysis report based on the following JD.com customer service chat records. Output the report body directly without self-introduction.

Data Overview:
  Total Conversations: {summary['total_conversations']}
  Date Range: {summary['date_range']}
  Customer Messages: {summary['total_customer_msgs']}
  Agent Messages: {summary['total_agent_msgs']}

Keyword Frequency TOP20:
{kw_str}

Negative Conversation Samples:
{sample_str}

Please output analysis in {len(custom_modules)} modules:
{modules_text}
{round_instruction}{extra_text}"""

    messages = [{"role": "user", "content": prompt}]
    
    # 多轮分析
    for round_idx in range(analysis_rounds):
        if round_idx > 0:
            if lang == "zh":
                deepen_prompt = f"请基于你上一轮的分析结论，进行第{round_idx+1}轮深化分析。要求：①指出前轮分析的不足或遗漏 ②补充新的数据视角或跨维度关联 ③更新风险判断和结论。保持原有模块结构，输出完整深化版报告。"
            else:
                deepen_prompt = f"Based on your previous round of analysis, conduct round {round_idx+1} of deepened analysis. Requirements: ① Identify gaps or omissions in the previous round ② Add new data perspectives or cross-dimensional correlations ③ Update risk assessments and conclusions. Maintain the original module structure and output the complete deepened report."
            messages.append({"role": "user", "content": deepen_prompt})
        
        resp = requests.post(
            f"{api_base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4000,
            },
            timeout=120,
        )
        
        if resp.status_code != 200:
            if lang == "zh":
                raise Exception(f"API调用失败(第{round_idx+1}轮): {resp.status_code} - {resp.text}")
            else:
                raise Exception(f"API call failed (round {round_idx+1}): {resp.status_code} - {resp.text}")
        ai_reply = resp.json()['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": ai_reply})
    
    if analysis_rounds > 1:
        if lang == "zh":
            return f"（经{analysis_rounds}轮深化分析）\n\n{ai_reply}"
        else:
            return f"(After {analysis_rounds} rounds of deepened analysis)\n\n{ai_reply}"
    return ai_reply
