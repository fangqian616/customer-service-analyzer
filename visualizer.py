#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海尔京东客服舆情分析系统 - 可视化模块
生成所有图表和PDF报告
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm
import numpy as np
import os
from collections import OrderedDict, Counter

# 中文字体：自动检测→下载→系统回退
_FONT_DIR = os.path.dirname(os.path.abspath(__file__))
_BUNDLED_FONT = os.path.join(_FONT_DIR, 'LXGWWenKai-Regular.ttf')
_FONT_DOWNLOAD_URL = 'https://github.com/lxgw/LxgwWenKai/releases/download/v1.501/LXGWWenKai-Regular.ttf'

def _ensure_font():
    """确保中文字体可用：自带→自动下载→系统字体→回退"""
    if os.path.exists(_BUNDLED_FONT):
        return _BUNDLED_FONT
    try:
        import urllib.request, sys
        print('首次运行，正在下载中文字体（约18MB，仅一次）...', file=sys.stderr)
        urllib.request.urlretrieve(_FONT_DOWNLOAD_URL, _BUNDLED_FONT)
        if os.path.getsize(_BUNDLED_FONT) > 1000000:
            print('字体下载完成！', file=sys.stderr)
            return _BUNDLED_FONT
        else:
            os.remove(_BUNDLED_FONT)
    except Exception:
        pass
    import platform as _pf
    system = _pf.system()
    candidates = []
    if system == 'Windows':
        font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
        for name in ['msyh.ttc', 'msyhbd.ttc', 'simhei.ttf', 'simsun.ttc']:
            p = os.path.join(font_dir, name)
            if os.path.exists(p):
                candidates.append(p)
    elif system == 'Darwin':
        for p in ['/System/Library/Fonts/PingFang.ttc', '/Library/Fonts/Arial Unicode.ttf']:
            if os.path.exists(p):
                candidates.append(p)
    else:
        for p in ['/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                   '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc']:
            if os.path.exists(p):
                candidates.append(p)
    for fp in candidates:
        try:
            return fp
        except Exception:
            continue
    return None

_font_path = _ensure_font()
if _font_path:
    try:
        fm.fontManager.addfont(_font_path)
        prop = fm.FontProperties(fname=_font_path)
        _found_cn = prop.get_name()
    except Exception:
        _found_cn = 'SimHei'
else:
    _found_cn = 'SimHei'
plt.rcParams['font.sans-serif'] = [_found_cn, 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

COLORS = {
    "blue": "#4C72B0", "orange": "#DD8452", "green": "#55A868",
    "red": "#C44E52", "purple": "#8172B3", "grey": "#937860",
    "gold": "#CCA64C", "light_blue": "#64B5CD",
}

POSITIVE_WORDS = {"好评", "满意", "正品", "推荐", "不错", "点赞"}
NEGATIVE_WORDS = {"退货", "退款", "质量", "维修", "制冷", "换货", "噪音", "结冰",
                  "投诉", "不制冷", "漏水", "赔偿", "不满", "故障", "坑", "损坏",
                  "异响", "差评", "失望", "假货", "骗", "坏了", "不工作"}


def add_text_box(fig, rect, title, body, title_color='#2C3E50', body_color='#333333'):
    """在figure上添加文字分析框"""
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_facecolor('#FAFAFA')
    for spine in ax.spines.values():
        spine.set_color('#DDD')
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.04, 0.92, title, fontsize=11, fontweight='bold', va='top', color=title_color, transform=ax.transAxes)
    ax.text(0.04, 0.80, body, fontsize=9, va='top', color=body_color, transform=ax.transAxes, linespacing=1.6)


def generate_pdf_report(parsed_data, output_path, ai_report_text=None):
    """
    生成完整的图文PDF报告
    
    Args:
        parsed_data: parser.py的输出
        output_path: PDF输出路径
        ai_report_text: 可选的AI分析文本
    """
    daily_stats = parsed_data['daily_stats']
    keyword_counts = parsed_data['keyword_counts']
    summary = _compute_summary(parsed_data)
    
    with PdfPages(output_path) as pdf:
        
        # ═══ Page 1: 封面 ═══
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor('#F7F7F7')
        fig.text(0.5, 0.82, '客服聊天记录', fontsize=32, fontweight='bold', ha='center', va='center', color='#2C3E50')
        fig.text(0.5, 0.72, '数据分析与舆情报告', fontsize=24, ha='center', va='center', color='#34495E')
        fig.text(0.5, 0.62, summary['date_range'], fontsize=16, ha='center', va='center', color='#7F8C8D')
        
        metrics = [
            ("会话总数", f"{summary['total_conversations']:,}", COLORS["blue"]),
            ("客户消息", f"{summary['total_customer_msgs']:,}", COLORS["orange"]),
            ("客服消息", f"{summary['total_agent_msgs']:,}", COLORS["green"]),
            ("客服人数", str(summary['num_agents']), COLORS["purple"]),
        ]
        card_w, card_h = 0.18, 0.18
        start_x = 0.5 - (len(metrics) * (card_w + 0.02) - 0.02) / 2
        for i, (label, value, color) in enumerate(metrics):
            x = start_x + i * (card_w + 0.02)
            ax = fig.add_axes([x, 0.28, card_w, card_h])
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_facecolor('white')
            for spine in ax.spines.values(): spine.set_visible(False)
            ax.set_xticks([]); ax.set_yticks([])
            ax.axhspan(0.88, 1.0, color=color, alpha=0.9)
            ax.text(0.5, 0.5, value, fontsize=28, fontweight='bold', ha='center', va='center', color=color)
            ax.text(0.5, 0.18, label, fontsize=12, ha='center', va='center', color='#7F8C8D')
        
        fig.text(0.5, 0.06, f'生成时间: {summary.get("gen_time", "")}', fontsize=9, ha='center', color='#95A5A6')
        pdf.savefig(fig); plt.close(fig)
        
        # ═══ Page 2: 每日趋势 ═══
        _page_daily_trend(pdf, daily_stats, summary)
        
        # ═══ Page 3: 关键词与情感 ═══
        _page_keywords(pdf, keyword_counts, summary)
        
        # ═══ Page 4: 负面深度 ═══
        _page_negative(pdf, keyword_counts)
        
        # ═══ Page 5: 咨询场景排名 ═══
        _page_scenarios(pdf, keyword_counts, summary)
        
        # ═══ Page 6: 场景拆解 ═══
        _page_scenario_detail(pdf, keyword_counts)
        
        # ═══ Page 7: 售前vs售后 ═══
        _page_presale_aftersale(pdf, daily_stats, keyword_counts, summary)
    
    # 如果有AI分析文本，追加到PDF
    if ai_report_text:
        _append_text_pages(output_path, ai_report_text)
    
    return output_path


def _compute_summary(parsed_data):
    """计算汇总数据"""
    from datetime import datetime
    daily_stats = parsed_data['daily_stats']
    keyword_counts = parsed_data['keyword_counts']
    
    dates = list(daily_stats.keys())
    conv_vals = [daily_stats[d]['conv'] for d in dates]
    cust_vals = [daily_stats[d]['customer'] for d in dates]
    
    pre_avg = np.mean(conv_vals[:max(1, len(conv_vals)//2)])
    post_avg = np.mean(conv_vals[max(1, len(conv_vals)//2+1):])
    
    pos_total = sum(v for k, v in keyword_counts.items() if k in POSITIVE_WORDS)
    neg_total = sum(v for k, v in keyword_counts.items() if k in NEGATIVE_WORDS)
    neu_total = sum(keyword_counts.values()) - pos_total - neg_total
    grand_total = sum(keyword_counts.values())
    
    return {
        'total_conversations': parsed_data['total_conversations'],
        'total_customer_msgs': sum(daily_stats[d]['customer'] for d in dates),
        'total_agent_msgs': sum(daily_stats[d]['agent'] for d in dates),
        'num_agents': len(parsed_data['agent_counter']),
        'date_range': f"{dates[0]} ~ {dates[-1]}" if len(dates) >= 2 else "N/A",
        'pre_avg': pre_avg,
        'post_avg': post_avg,
        'pos_total': pos_total,
        'neg_total': neg_total,
        'neu_total': neu_total,
        'grand_total': grand_total,
        'dates': dates,
        'conv_vals': conv_vals,
        'cust_vals': cust_vals,
        'gen_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }


def _page_daily_trend(pdf, daily_stats, summary):
    """每日趋势页"""
    dates = [d[5:] for d in summary['dates']]  # 去掉年份
    conv_vals = summary['conv_vals']
    cust_vals = summary['cust_vals']
    agent_vals = [daily_stats[d]['agent'] for d in summary['dates']]
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '一、每日会话与消息趋势', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    ax1 = fig.add_axes([0.06, 0.54, 0.55, 0.38])
    ax1.bar(dates, conv_vals, color=COLORS["blue"], alpha=0.85, width=0.7)
    ax1.set_ylabel('会话数', fontsize=10)
    ax1.set_title('每日会话量', fontsize=12, pad=8)
    if conv_vals:
        peak_idx = conv_vals.index(max(conv_vals))
        ax1.annotate(str(max(conv_vals)), xy=(peak_idx, max(conv_vals)),
                    xytext=(min(peak_idx+1, len(dates)-1), max(conv_vals)+50),
                    arrowprops=dict(arrowstyle='->', color=COLORS["red"]),
                    fontsize=10, fontweight='bold', color=COLORS["red"])
    ax1.grid(axis='y', alpha=0.3)
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    
    ax2 = fig.add_axes([0.06, 0.08, 0.55, 0.38])
    x_pos = np.arange(len(dates))
    width = 0.38
    ax2.bar(x_pos - width/2, cust_vals, width, color=COLORS["orange"], alpha=0.85, label='客户消息')
    ax2.bar(x_pos + width/2, agent_vals, width, color=COLORS["green"], alpha=0.85, label='客服消息')
    ax2.set_xticks(x_pos); ax2.set_xticklabels(dates, fontsize=8)
    ax2.set_ylabel('消息数', fontsize=10)
    ax2.set_title('每日客户 vs 客服消息量', fontsize=12, pad=8)
    ax2.legend(fontsize=9); ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    
    peak_val = max(conv_vals) if conv_vals else 0
    ratio_avg = np.mean([a/c if c > 0 else 0 for a, c in zip(agent_vals, cust_vals)]) if cust_vals else 0
    text_body = (
        f'▸ 峰值日会话量{peak_val}通\n\n'
        f'▸ 大促前日均{summary["pre_avg"]:.0f}通，大促后日均{summary["post_avg"]:.0f}通\n\n'
        f'▸ 客户/客服消息比约1:{ratio_avg:.1f}\n\n'
        f'▸ 数据周期共{len(dates)}天'
    )
    add_text_box(fig, [0.66, 0.08, 0.30, 0.84], '趋势分析', text_body)
    pdf.savefig(fig); plt.close(fig)


def _page_keywords(pdf, keyword_counts, summary):
    """关键词与情感页"""
    if not keyword_counts:
        return
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '二、关键词频次与情感分析', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    top15 = keyword_counts.most_common(15)
    top15.reverse()
    kw_names = [k for k, v in top15]
    kw_vals = [v for k, v in top15]
    bar_colors = []
    for k in kw_names:
        if k in NEGATIVE_WORDS: bar_colors.append(COLORS["red"])
        elif k in POSITIVE_WORDS: bar_colors.append(COLORS["green"])
        else: bar_colors.append(COLORS["blue"])
    
    ax1 = fig.add_axes([0.06, 0.30, 0.42, 0.60])
    ax1.barh(kw_names, kw_vals, color=bar_colors, alpha=0.85, height=0.65)
    ax1.set_xlabel('频次', fontsize=10)
    ax1.set_title('关键词 TOP15', fontsize=12, pad=8)
    for i, v in enumerate(kw_vals):
        ax1.text(v + max(kw_vals)*0.01, i, str(v), va='center', fontsize=8, color='#555')
    ax1.grid(axis='x', alpha=0.3)
    
    ax2 = fig.add_axes([0.52, 0.30, 0.18, 0.60])
    pos_t = summary['pos_total']
    neg_t = summary['neg_total']
    neu_t = summary['neu_total']
    sizes = [neu_t, neg_t, pos_t]
    labels = [f'中性\n{neu_t}', f'负面\n{neg_t}', f'正面\n{pos_t}']
    pie_colors = [COLORS["blue"], COLORS["red"], COLORS["green"]]
    explode = (0, 0.06, 0.03)
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=pie_colors, explode=explode,
                                        autopct='%1.1f%%', startangle=140, textprops={'fontsize': 9})
    for at in autotexts: at.set_fontsize(8); at.set_color('white'); at.set_fontweight('bold')
    ax2.set_title('情感分类', fontsize=12, pad=8)
    
    total = pos_t + neg_t + neu_t
    text_body = (
        f'▸ 中性咨询占比{neu_t/total*100:.1f}%\n\n'
        f'▸ 负面情绪关键词合计{neg_t}次（{neg_t/total*100:.1f}%）\n\n'
        f'▸ 正面情绪关键词{pos_t}次（{pos_t/total*100:.1f}%）\n\n'
        f'▸ 蓝色=中性 红色=负面 绿色=正面'
    )
    add_text_box(fig, [0.06, 0.04, 0.88, 0.22], '分析结论', text_body)
    pdf.savefig(fig); plt.close(fig)


def _page_negative(pdf, keyword_counts):
    """负面深度分析页"""
    neg_kw = {k: v for k, v in keyword_counts.items() if k in NEGATIVE_WORDS}
    if not neg_kw:
        return
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '三、负面情绪深度分析', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    neg_sorted = sorted(neg_kw.items(), key=lambda x: x[1], reverse=True)
    neg_names = [k for k, v in neg_sorted]
    neg_vals = [v for k, v in neg_sorted]
    
    ax1 = fig.add_axes([0.06, 0.35, 0.42, 0.56])
    red_gradient = plt.cm.Reds(np.linspace(0.35, 0.85, len(neg_names)))
    ax1.barh(neg_names[::-1], neg_vals[::-1], color=red_gradient, height=0.65, alpha=0.9)
    ax1.set_xlabel('频次', fontsize=10)
    ax1.set_title('负面关键词频次排行', fontsize=12, pad=8)
    for i, v in enumerate(neg_vals[::-1]):
        ax1.text(v + 1, i, str(v), va='center', fontsize=8, color='#555')
    ax1.grid(axis='x', alpha=0.3)
    
    # 问题分类归集
    ax2 = fig.add_axes([0.54, 0.35, 0.40, 0.56])
    cats = OrderedDict([
        ("售后流程", sum(neg_kw.get(k, 0) for k in ["退货", "退款", "换货", "投诉", "赔偿"])),
        ("产品质量", sum(neg_kw.get(k, 0) for k in ["质量", "制冷", "不制冷", "故障", "损坏"])),
        ("使用异常", sum(neg_kw.get(k, 0) for k in ["噪音", "结冰", "漏水", "异响"])),
        ("情绪表达", sum(neg_kw.get(k, 0) for k in ["不满", "坑", "差评", "失望", "假货", "骗"])),
    ])
    cat_colors = [COLORS["red"], COLORS["orange"], COLORS["gold"], COLORS["purple"]]
    bars = ax2.bar(list(cats.keys()), list(cats.values()), color=cat_colors, alpha=0.85, width=0.55)
    for bar, val in zip(bars, cats.values()):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(val), ha='center', fontsize=11, fontweight='bold', color='#333')
    ax2.set_ylabel('频次合计', fontsize=10)
    ax2.set_title('负面问题分类归集', fontsize=12, pad=8)
    ax2.grid(axis='y', alpha=0.3)
    
    neg_total = sum(neg_vals)
    top_neg = neg_sorted[0] if neg_sorted else ("N/A", 0)
    text_body = (
        f'▸ 负面关键词合计{neg_total}次\n\n'
        f'▸ 最高频负面词: {top_neg[0]}({top_neg[1]}次)\n\n'
        f'▸ 售后流程问题占负面{cats["售后流程"]/neg_total*100:.1f}%\n\n'
        f'▸ 建议优先改善退货退款流程和售后响应时效'
    )
    add_text_box(fig, [0.06, 0.04, 0.88, 0.26], '负面分析结论', text_body)
    pdf.savefig(fig); plt.close(fig)


def _page_scenarios(pdf, keyword_counts, summary):
    """咨询场景排名页"""
    from parser import KEYWORD_CATEGORIES
    
    scenarios = OrderedDict()
    for cat, kws in KEYWORD_CATEGORIES.items():
        total = sum(keyword_counts.get(kw, 0) for kw in kws)
        if total > 0:
            scenarios[cat] = {kw: keyword_counts.get(kw, 0) for kw in kws if keyword_counts.get(kw, 0) > 0}
    
    scenario_sorted = sorted(scenarios.items(), key=lambda x: sum(x[1].values()), reverse=True)
    s_names = [s[0] for s in scenario_sorted]
    s_totals = [sum(s[1].values()) for s in scenario_sorted]
    grand_total = sum(s_totals)
    
    if not s_names:
        return
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '四、用户咨询场景分类排名', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    scenario_colors = []
    for name in s_names:
        if name in ["好评满意"]: scenario_colors.append(COLORS["green"])
        elif name in ["售后退换", "产品质量", "维修保修", "投诉不满"]: scenario_colors.append(COLORS["red"])
        elif name in ["物流配送", "安装服务", "发票开票"]: scenario_colors.append(COLORS["orange"])
        else: scenario_colors.append(COLORS["blue"])
    
    ax1 = fig.add_axes([0.06, 0.28, 0.50, 0.62])
    s_names_rev = s_names[::-1]
    s_totals_rev = s_totals[::-1]
    sc_rev = scenario_colors[::-1]
    ax1.barh(s_names_rev, s_totals_rev, color=sc_rev, alpha=0.85, height=0.65)
    ax1.set_xlabel('咨询频次', fontsize=10)
    ax1.set_title('用户咨询场景排名（从高到低）', fontsize=12, pad=8)
    for i, v in enumerate(s_totals_rev):
        ax1.text(v + max(s_totals)*0.01, i, f'{v} ({v/grand_total*100:.1f}%)', va='center', fontsize=8, color='#333')
    ax1.grid(axis='x', alpha=0.3)
    
    ax2 = fig.add_axes([0.58, 0.28, 0.38, 0.62])
    top_n = min(6, len(s_names))
    topn = s_names[:top_n]
    topn_vals = s_totals[:top_n]
    other_val = sum(s_totals[top_n:])
    pie_labels = topn + ['其他'] if other_val > 0 else topn
    pie_vals = topn_vals + [other_val] if other_val > 0 else topn_vals
    pie_colors_list = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860', '#95A5A6']
    explode_pie = [0.03] * len(pie_vals)
    wedges, texts, autotexts = ax2.pie(
        pie_vals, labels=[f'{l}\n{v}' for l, v in zip(pie_labels, pie_vals)],
        colors=pie_colors_list[:len(pie_vals)], explode=explode_pie,
        autopct='%1.1f%%', startangle=140, textprops={'fontsize': 9}
    )
    for at in autotexts: at.set_fontsize(8); at.set_color('white'); at.set_fontweight('bold')
    ax2.set_title('咨询场景占比', fontsize=12, pad=8)
    
    top3_pct = sum(s_totals[:3]) / grand_total * 100 if grand_total > 0 else 0
    text_body = (
        f'▸ TOP3场景合计占全部咨询{top3_pct:.1f}%\n\n'
        f'▸ 蓝色=售前 橙色=履约 红色=售后 绿色=正面'
    )
    add_text_box(fig, [0.06, 0.04, 0.88, 0.20], '场景分析结论', text_body)
    pdf.savefig(fig); plt.close(fig)


def _page_scenario_detail(pdf, keyword_counts):
    """场景子关键词拆解"""
    from parser import KEYWORD_CATEGORIES
    
    scenarios = OrderedDict()
    for cat, kws in KEYWORD_CATEGORIES.items():
        detail = {kw: keyword_counts.get(kw, 0) for kw in kws if keyword_counts.get(kw, 0) > 0}
        if detail:
            scenarios[cat] = detail
    
    multi_kw = [(n, d) for n, d in scenarios.items() if len(d) > 1]
    if not multi_kw:
        return
    
    multi_kw.sort(key=lambda x: sum(x[1].values()), reverse=True)
    multi_kw = multi_kw[:8]
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '五、多关键词场景拆解', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    row1 = multi_kw[:4]
    row2 = multi_kw[4:8]
    
    for ri, row_data in enumerate([row1, row2]):
        for ci, (name, detail) in enumerate(row_data):
            ax = fig.add_axes([0.06 + ci * 0.235, 0.52 - ri * 0.44, 0.22, 0.40])
            items = sorted(detail.items(), key=lambda x: x[1], reverse=True)
            kws = [k for k, v in items]
            vals = [v for k, v in items]
            bar_c = COLORS["red"] if name in ["售后退换", "产品质量", "投诉不满"] else COLORS["blue"]
            ax.bar(kws, vals, color=bar_c, alpha=0.8, width=0.55)
            for i2, v in enumerate(vals):
                ax.text(i2, v + max(vals)*0.03, str(v), ha='center', fontsize=7, color='#333')
            ax.set_title(name, fontsize=10, fontweight='bold', pad=6)
            ax.tick_params(axis='x', labelsize=7, rotation=20)
            ax.tick_params(axis='y', labelsize=7)
            ax.grid(axis='y', alpha=0.3)
    
    pdf.savefig(fig); plt.close(fig)


def _page_presale_aftersale(pdf, daily_stats, keyword_counts, summary):
    """售前vs售后对比"""
    presale_kw = OrderedDict()
    aftersale_kw = OrderedDict()
    
    from parser import KEYWORD_CATEGORIES
    presale_cats = {"物流配送", "价格与优惠", "产品选型", "促销赠品", "正品验证"}
    aftersale_cats = {"售后退换", "产品质量", "维修保修", "投诉不满", "安装服务", "发票开票"}
    
    for cat, kws in KEYWORD_CATEGORIES.items():
        for kw in kws:
            cnt = keyword_counts.get(kw, 0)
            if cnt > 0:
                if cat in presale_cats:
                    presale_kw[kw] = cnt
                elif cat in aftersale_cats:
                    aftersale_kw[kw] = cnt
    
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.97, '六、售前售后对比分析', fontsize=16, fontweight='bold', ha='center', va='top', color='#2C3E50')
    
    # 售前vs售后关键词对比
    ax1 = fig.add_axes([0.06, 0.40, 0.42, 0.50])
    all_kw = list(presale_kw.keys())[:6] + list(aftersale_kw.keys())[:6]
    presale_vals = [presale_kw.get(k, 0) for k in all_kw]
    aftersale_vals = [aftersale_kw.get(k, 0) for k in all_kw]
    x_pos = np.arange(len(all_kw))
    width = 0.35
    ax1.bar(x_pos - width/2, presale_vals, width, color=COLORS["blue"], alpha=0.85, label='售前咨询')
    ax1.bar(x_pos + width/2, aftersale_vals, width, color=COLORS["red"], alpha=0.85, label='售后问题')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(all_kw, fontsize=7, rotation=30)
    ax1.set_ylabel('频次', fontsize=10)
    ax1.set_title('售前咨询 vs 售后问题', fontsize=12, pad=8)
    ax1.legend(fontsize=9); ax1.grid(axis='y', alpha=0.3)
    
    # 售前售后总量对比饼图
    ax2 = fig.add_axes([0.54, 0.40, 0.40, 0.50])
    presale_total = sum(presale_kw.values())
    aftersale_total = sum(aftersale_kw.values())
    sizes = [presale_total, aftersale_total]
    labels = [f'售前咨询\n{presale_total}', f'售后问题\n{aftersale_total}']
    pie_colors = [COLORS["blue"], COLORS["red"]]
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=pie_colors,
                                        autopct='%1.1f%%', startangle=140, explode=(0.03, 0.03),
                                        textprops={'fontsize': 11})
    for at in autotexts: at.set_fontsize(10); at.set_color('white'); at.set_fontweight('bold')
    ax2.set_title('售前/售后占比', fontsize=12, pad=8)
    
    ratio = presale_total / aftersale_total if aftersale_total > 0 else 0
    text_body = (
        f'▸ 售前咨询{presale_total}次 vs 售后问题{aftersale_total}次\n\n'
        f'▸ 售前/售后比 = {ratio:.1f}:1\n\n'
        f'▸ 大促期间售前咨询占主导\n\n'
        f'▸ 大促后售后问题比例上升'
    )
    add_text_box(fig, [0.06, 0.04, 0.88, 0.30], '对比分析', text_body)
    pdf.savefig(fig); plt.close(fig)


def _append_text_pages(pdf_path, text_content):
    """将AI分析文本追加到PDF末尾"""
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    import re, os, tempfile
    
    FONT_NAME = 'LXGW'
    try:
        if os.path.exists(_BUNDLED_FONT):
            pdfmetrics.registerFont(TTFont(FONT_NAME, _BUNDLED_FONT))
        else:
            # 回退：系统字体
            import platform
            system = platform.system()
            _found = False
            if system == 'Windows':
                font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
                for name in ['msyh.ttc', 'simhei.ttf', 'simsun.ttc']:
                    p = os.path.join(font_dir, name)
                    if os.path.exists(p):
                        try:
                            pdfmetrics.registerFont(TTFont('SysCN', p))
                            FONT_NAME = 'SysCN'
                            _found = True
                            break
                        except Exception:
                            continue
            if not _found:
                FONT_NAME = 'Helvetica'
    except:
        FONT_NAME = 'Helvetica'
    
    tmp_path = tempfile.mktemp(suffix='.pdf')
    doc = SimpleDocTemplate(tmp_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName=FONT_NAME, fontSize=14, leading=20, spaceBefore=14, spaceAfter=6, textColor='#C44E52')
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontName=FONT_NAME, fontSize=12, leading=17, spaceBefore=10, spaceAfter=4, textColor='#34495E')
    body_style = ParagraphStyle('BD', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9.5, leading=15, spaceBefore=2, spaceAfter=4, alignment=TA_JUSTIFY, textColor='#333333')
    bullet_style = ParagraphStyle('BL', parent=body_style, leftIndent=15, bulletIndent=0, spaceBefore=1, spaceAfter=2)
    
    def clean(text):
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = text.replace('*', '')
        return text
    
    story = []
    for line in text_content.split('\n'):
        line = line.rstrip()
        if not line: continue
        if line.startswith('### '):
            story.append(Paragraph(clean(line[4:].strip()), h3_style))
        elif line.startswith('## '):
            story.append(HRFlowable(width="100%", thickness=1, color='#DDD'))
            story.append(Paragraph(clean(line[3:].strip()), h2_style))
        elif line.startswith('---'):
            story.append(HRFlowable(width="100%", thickness=1, color='#DDD', spaceBefore=8, spaceAfter=8))
        elif line.strip().startswith('- '):
            story.append(Paragraph('• ' + clean(line.strip()[2:].strip()), bullet_style))
        else:
            ol = re.match(r'^\s*(\d+)\.\s+(.*)', line)
            if ol:
                story.append(Paragraph(f'{ol.group(1)}. {clean(ol.group(2).strip())}', bullet_style))
            else:
                story.append(Paragraph(clean(line.strip()), body_style))
    
    doc.build(story)
    
    # 合并
    writer = PdfWriter()
    r1 = PdfReader(pdf_path)
    r2 = PdfReader(tmp_path)
    for p in r1.pages: writer.add_page(p)
    for p in r2.pages: writer.add_page(p)
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    
    os.unlink(tmp_path)
