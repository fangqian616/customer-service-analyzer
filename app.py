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

from parser import parse_log_file, get_summary_stats, KEYWORD_CATEGORIES, NEGATIVE_WORDS
from visualizer import generate_pdf_report

# ── 页面配置 ──
st.set_page_config(
    page_title="客服舆情分析系统",
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
    st.image("https://img.icons8.com/fluency/96/chat.png", width=60)
    st.title("客服舆情分析")
    st.caption("上传聊天记录，一键生成分析报告")
    
    st.divider()
    
    # DeepSeek API（可选）
    st.subheader("AI分析（可选）")
    deepseek_key = st.text_input("DeepSeek API Key", type="password", 
                                  help="填入后可生成AI深度分析文本，留空则仅生成数据报告")
    deepseek_base = st.text_input("API Base URL", value="https://api.deepseek.com/v1",
                                   help="默认使用DeepSeek官方，也可替换为兼容接口")
    
    st.divider()
    
    # 解析参数
    st.subheader("解析参数")
    max_conv = st.number_input("最大解析会话数", min_value=100, max_value=100000, 
                                value=20000, step=5000, help="限制解析数量以加快速度")
    encoding = st.selectbox("文件编码", ["utf-8", "gbk", "gb2312", "utf-16"], index=0)

# ── 主区域 ──
st.markdown('<p class="main-title">📊 客服聊天记录舆情分析系统</p>', unsafe_allow_html=True)
st.markdown("上传飞书导出的聊天记录文件，自动完成数据解析、关键词提取、可视化分析，一键导出PDF报告。")

# ── 文件上传 ──
uploaded_file = st.file_uploader(
    "上传聊天记录文件",
    type=["log", "txt", "csv"],
    help="支持飞书导出的聊天记录格式（.log / .txt）"
)

if uploaded_file is not None:
    # 保存上传文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    # ── 解析数据 ──
    with st.spinner("正在解析聊天记录..."):
        t0 = time.time()
        try:
            parsed = parse_log_file(tmp_path, encoding=encoding, max_conversations=max_conv)
            summary = get_summary_stats(parsed)
            parse_time = time.time() - t0
            st.success(f"解析完成！耗时 {parse_time:.1f}s，共 {summary['total_conversations']:,} 条会话")
        except Exception as e:
            st.error(f"解析失败：{e}")
            st.stop()
    
    # ── 概览指标 ──
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("会话总数", f"{summary['total_conversations']:,}")
    with col2:
        st.metric("客户消息", f"{summary['total_customer_msgs']:,}")
    with col3:
        st.metric("客服消息", f"{summary['total_agent_msgs']:,}")
    with col4:
        st.metric("客服人数", str(summary['num_agents']))
    with col5:
        st.metric("数据周期", summary['date_range'])
    
    # ── Tab区域 ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 每日趋势", "🔑 关键词分析", "⚠️ 负面深度", 
        "📋 场景排名", "📥 导出报告"
    ])
    
    # ═══ Tab1: 每日趋势 ═══
    with tab1:
        st.subheader("每日会话与消息趋势")
        
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
            ax1.set_title('每日会话量', fontsize=13)
            ax1.set_ylabel('会话数')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(axis='y', alpha=0.3)
            
            x_pos = np.arange(len(dates))
            ax2.bar(x_pos - 0.19, cust_vals, 0.38, color='#DD8452', alpha=0.85, label='客户')
            ax2.bar(x_pos + 0.19, agent_vals, 0.38, color='#55A868', alpha=0.85, label='客服')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(short_dates, fontsize=8)
            ax2.set_title('客户 vs 客服消息量', fontsize=13)
            ax2.legend()
            ax2.grid(axis='y', alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 日均统计
            col1, col2, col3 = st.columns(3)
            if conv_vals:
                col1.metric("峰值日会话", f"{max(conv_vals):,}", f"{dates[conv_vals.index(max(conv_vals))]}")
                col2.metric("日均会话", f"{np.mean(conv_vals):.0f}")
                col3.metric("客服/客户比", f"{np.mean(agent_vals)/max(np.mean(cust_vals),1):.1f}")
    
    # ═══ Tab2: 关键词分析 ═══
    with tab2:
        st.subheader("关键词频次与情感分析")
        
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
            ax1.set_title('关键词 TOP15', fontsize=13)
            for i, v in enumerate(vals):
                ax1.text(v + max(vals)*0.01, i, str(v), va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 情感饼图
            pos_t = sum(v for k, v in kw.items() if k in POSITIVE_WORDS)
            neg_t = sum(v for k, v in kw.items() if k in NEGATIVE_WORDS)
            neu_t = sum(kw.values()) - pos_t - neg_t
            ax2.pie([neu_t, neg_t, pos_t], 
                    labels=[f'中性 {neu_t}', f'负面 {neg_t}', f'正面 {pos_t}'],
                    colors=['#4C72B0', '#C44E52', '#55A868'],
                    autopct='%1.1f%%', startangle=140)
            ax2.set_title('情感分类', fontsize=13)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 关键词表格
            st.subheader("关键词频次表")
            kw_df_data = [{"关键词": k, "频次": v, "情感": "负面" if k in NEGATIVE_WORDS else ("正面" if k in POSITIVE_WORDS else "中性")} 
                          for k, v in kw.most_common(30)]
            st.dataframe(kw_df_data, use_container_width=True, hide_index=True)
    
    # ═══ Tab3: 负面深度 ═══
    with tab3:
        st.subheader("负面情绪深度分析")
        
        neg_kw = {k: v for k, v in kw.items() if k in NEGATIVE_WORDS}
        if neg_kw:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
            
            neg_sorted = sorted(neg_kw.items(), key=lambda x: x[1], reverse=True)
            n_names = [k for k, v in neg_sorted]
            n_vals = [v for k, v in neg_sorted]
            red_grad = plt.cm.Reds(np.linspace(0.35, 0.85, len(n_names)))
            ax1.barh(n_names[::-1], n_vals[::-1], color=red_grad, height=0.65, alpha=0.9)
            ax1.set_title('负面关键词排行', fontsize=13)
            for i, v in enumerate(n_vals[::-1]):
                ax1.text(v + 1, i, str(v), va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 问题分类
            from collections import OrderedDict
            cats = OrderedDict([
                ("售后流程", sum(neg_kw.get(k, 0) for k in ["退货", "退款", "换货", "投诉", "赔偿"])),
                ("产品质量", sum(neg_kw.get(k, 0) for k in ["质量", "制冷", "不制冷", "故障", "损坏"])),
                ("使用异常", sum(neg_kw.get(k, 0) for k in ["噪音", "结冰", "漏水", "异响"])),
                ("情绪表达", sum(neg_kw.get(k, 0) for k in ["不满", "坑", "差评", "失望", "假货", "骗"])),
            ])
            cat_colors = ['#C44E52', '#DD8452', '#CCA64C', '#8172B3']
            bars = ax2.bar(list(cats.keys()), list(cats.values()), color=cat_colors, alpha=0.85, width=0.55)
            for bar, val in zip(bars, cats.values()):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val),
                        ha='center', fontsize=11, fontweight='bold')
            ax2.set_title('负面问题分类归集', fontsize=13)
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 负面对话样本
            st.subheader("负面对话样本")
            sample = parsed['sample_negative'][:10]
            for i, conv in enumerate(sample):
                customer_msgs = [m['content'] for m in conv if m['role'] == 'customer']
                if customer_msgs:
                    with st.expander(f"样本 {i+1}"):
                        for msg in customer_msgs[:5]:
                            st.markdown(f"👤 {msg}")
    
    # ═══ Tab4: 场景排名 ═══
    with tab4:
        st.subheader("用户咨询场景分类排名")
        
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
            ax1.set_title('咨询场景排名（从高到低）', fontsize=13)
            for i, v in enumerate(s_totals_rev):
                ax1.text(v + max(s_totals)*0.01, i, f'{v} ({v/grand_total*100:.1f}%)', va='center', fontsize=8)
            ax1.grid(axis='x', alpha=0.3)
            
            # 饼图
            top_n = min(6, len(s_names))
            pie_labels = s_names[:top_n] + ['其他']
            pie_vals = s_totals[:top_n] + [sum(s_totals[top_n:])]
            pie_c = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860', '#95A5A6']
            ax2.pie(pie_vals, labels=[f'{l}\n{v}' for l, v in zip(pie_labels, pie_vals)],
                    colors=pie_c[:len(pie_vals)], autopct='%1.1f%%', startangle=140)
            ax2.set_title('场景占比分布', fontsize=13)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 场景详情表
            st.subheader("场景详情")
            for name, detail in scenario_sorted:
                total = sum(detail.values())
                sub_str = "、".join(f"{k}({v})" for k, v in sorted(detail.items(), key=lambda x: x[1], reverse=True))
                st.markdown(f"**{name}** — 合计 {total} 次  \n{sub_str}")
    
    # ═══ Tab5: 导出报告 ═══
    with tab5:
        st.subheader("导出PDF报告")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 数据可视化报告")
            st.markdown("包含7页图表：封面、每日趋势、关键词分析、负面深度、场景排名、场景拆解、售前售后对比")
            
            if st.button("生成数据报告", key="gen_data"):
                with st.spinner("正在生成PDF..."):
                    try:
                        pdf_tmp = tempfile.mktemp(suffix='.pdf')
                        generate_pdf_report(parsed, pdf_tmp)
                        with open(pdf_tmp, 'rb') as f:
                            st.download_button(
                                label="📥 下载数据报告",
                                data=f.read(),
                                file_name=f"客服舆情分析_数据报告_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"生成失败: {e}")
        
        with col2:
            st.markdown("#### 📊+📝 完整分析报告")
            st.markdown("数据图表 + AI深度分析文本（需要DeepSeek API Key）")
            
            if not deepseek_key:
                st.warning("请先在侧边栏填入DeepSeek API Key")
            
            if st.button("生成完整报告", key="gen_full", disabled=not deepseek_key):
                with st.spinner("正在调用AI分析..."):
                    try:
                        # 调用DeepSeek API
                        ai_text = _call_deepseek(deepseek_key, deepseek_base, parsed, summary)
                        
                        pdf_tmp = tempfile.mktemp(suffix='.pdf')
                        generate_pdf_report(parsed, pdf_tmp, ai_report_text=ai_text)
                        
                        with open(pdf_tmp, 'rb') as f:
                            st.download_button(
                                label="📥 下载完整报告",
                                data=f.read(),
                                file_name=f"客服舆情分析_完整报告_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.error(f"生成失败: {e}")
    
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
        st.info("""
        ### 📤 使用说明
        
        1. 将飞书导出的聊天记录文件（.log / .txt）拖到上方上传区
        2. 系统自动解析数据并展示交互式图表
        3. 切换到「导出报告」Tab，一键生成PDF报告
        
        **支持的格式：** 飞书导出的客服聊天记录
        
        **功能：**
        - 每日会话趋势分析
        - 关键词频次统计与情感分类
        - 负面情绪深度分析与对话样本
        - 13类咨询场景自动分类排名
        - 售前/售后对比分析
        - 可选接入DeepSeek AI生成深度分析文本
        """)


def _call_deepseek(api_key, api_base, parsed_data, summary):
    """调用DeepSeek API生成分析文本"""
    import requests
    
    keyword_counts = parsed_data['keyword_counts']
    top_kw = keyword_counts.most_common(20)
    kw_str = "\n".join(f"  {k}: {v}次" for k, v in top_kw)
    
    # 构建负面对话样本
    sample_str = ""
    for i, conv in enumerate(parsed_data['sample_negative'][:15]):
        sample_str += f"\n--- 会话{i+1} ---\n"
        for msg in conv[:6]:
            role = "客服" if msg['role'] == 'agent' else "客户"
            sample_str += f"[{msg.get('date', '')}] {role}: {msg['content']}\n"
    
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

请输出8个模块的分析：
### 1. 整体舆情态势
### 2. 核心痛点TOP5（每个痛点配3条典型原话）
### 3. 产品质量问题汇总
### 4. 服务体验问题
### 5. 国补/促销政策相关舆情
### 6. 情感分布判断
### 7. 风险预警
### 8. 改进建议"""

    resp = requests.post(
        f"{api_base}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        timeout=120
    )
    
    if resp.status_code == 200:
        return resp.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"API调用失败: {resp.status_code} - {resp.text}")
