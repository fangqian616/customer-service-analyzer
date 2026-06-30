#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海尔京东客服舆情分析系统 - 日志解析模块
支持飞书导出的聊天记录格式
"""

import re
from collections import OrderedDict, Counter
from datetime import datetime


# ── 预设关键词库 ──
KEYWORD_CATEGORIES = {
    "物流配送": ["发货", "物流", "快递", "配送", "到货", "送货", "签收", "揽收"],
    "价格与优惠": ["优惠", "价格", "差价", "国补", "补贴", "折扣", "降价", "满减", "优惠卷", "优惠券"],
    "产品选型": ["尺寸", "型号", "颜色", "容量", "规格", "功率"],
    "促销赠品": ["赠品", "礼品", "送", "附赠"],
    "安装服务": ["安装", "上门", "预约"],
    "发票开票": ["发票", "开票", "税票"],
    "正品验证": ["正品", "假货", "真伪", "仿冒"],
    "客服咨询": ["客服", "推荐", "咨询", "建议"],
    "售后退换": ["退货", "退款", "换货", "赔偿", "退回", "退换"],
    "产品质量": ["质量", "制冷", "不制冷", "噪音", "结冰", "漏水", "故障", "损坏", "异响", "不工作", "坏了"],
    "好评满意": ["好评", "满意", "点赞", "不错"],
    "维修保修": ["维修", "保修", "质保", "报修"],
    "投诉不满": ["投诉", "不满", "坑", "差评", "失望", "骗"],
}

# 情感分类
POSITIVE_WORDS = {"好评", "满意", "正品", "推荐", "不错", "点赞"}
NEGATIVE_WORDS = {"退货", "退款", "质量", "维修", "制冷", "换货", "噪音", "结冰",
                  "投诉", "不制冷", "漏水", "赔偿", "不满", "故障", "坑", "损坏",
                  "异响", "差评", "失望", "假货", "骗", "坏了", "不工作"}


def parse_log_file(filepath, encoding='utf-8', max_conversations=None):
    """
    解析飞书导出的聊天记录日志文件
    
    格式特征：
    - 每行以 \t 结尾
    - 发言人行格式：ID\t时间\t（或带系统标记）
    - 内容行格式：消息内容\t
    
    返回: {
        'conversations': [...],
        'daily_stats': OrderedDict,
        'keyword_counts': Counter,
        'agent_counts': Counter,
        'sample_negative': [...],
    }
    """
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        lines = f.readlines()
    
    conversations = []
    current_conv = []
    current_date = None
    agent_counter = Counter()
    
    # 客服行特征：以 #E-s 开头、~ 开头、或 "海尔xxx + 时间" 格式
    agent_pattern = re.compile(r'^(#E-s|~|海尔[\u4e00-\u9fff]+[\s\d:]+)')
    # 时间行特征
    time_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}')
    
    last_speaker = None  # 'customer' or 'agent'
    msg_buffer = []
    
    for raw_line in lines:
        line = raw_line.strip('\t\n\r')
        if not line:
            continue
        
        # 检测新会话分隔（连续两个空行或特定标记）
        # 这里简化处理：按时间行判断
        
        # 检测时间
        time_match = time_pattern.search(line)
        if time_match:
            date_str = time_match.group(1)
            
            # 判断是客户还是客服行
            is_agent = bool(agent_pattern.match(line))
            
            if not is_agent and line.count('\t') <= 2:
                # 可能是客户发言行（ID + 时间）
                is_agent = False
            
            # 提取时间戳后的消息（如果有）
            parts = line.split('\t')
            
            last_speaker = 'agent' if is_agent else 'customer'
            current_date = date_str
            
            # 提取消息内容（时间行后面通常跟内容行）
            continue
        
        # 非时间行 = 消息内容
        if last_speaker and line:
            msg = line.strip()
            if msg:
                if last_speaker == 'agent':
                    # 提取客服名称
                    pass  # 简化处理
                
                current_conv.append({
                    'role': last_speaker,
                    'content': msg,
                    'date': current_date,
                })
    
    # 如果简单解析不够，使用更健壮的方法
    return _parse_robust(filepath, encoding, max_conversations)


def _parse_robust(filepath, encoding, max_conversations):
    """更健壮的解析方法：逐行追踪状态机"""
    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
        lines = f.readlines()
    
    conversations = []
    current_conv = []
    current_date = None
    agent_counter = Counter()
    daily_data = {}  # date -> {conv, customer, agent}
    
    last_speaker = None
    conv_id = 0
    last_msg_had_time = False
    
    agent_pattern = re.compile(r'^(#E-s\d*|~\s|海尔[\u4e00-\u9fff]+\s+\d)')
    time_in_line = re.compile(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})')
    system_msg = re.compile(r'^(#E-s\d*|系统提示|会话结束|会话开始)')
    
    for raw_line in lines:
        line = raw_line.strip('\t\n\r ')
        if not line:
            # 空行可能是会话分隔
            if current_conv and len(current_conv) >= 2:
                conversations.append(current_conv[:])
                conv_id += 1
                current_conv = []
                if max_conversations and conv_id >= max_conversations:
                    break
            continue
        
        # 检测时间
        t = time_in_line.search(line)
        if t:
            year, month, day = t.group(1), t.group(2), t.group(3)
            current_date = f"{year}-{month}-{day}"
            
            if current_date not in daily_data:
                daily_data[current_date] = {'conv': 0, 'customer': 0, 'agent': 0, 'conv_started': False}
            
            # 判断是否客服行
            is_agent = bool(agent_pattern.match(line))
            
            last_speaker = 'agent' if is_agent else 'customer'
            last_msg_had_time = True
            
            # 记录客服名
            if is_agent:
                # 尝试提取客服名
                parts = line.split('\t')
                if len(parts) >= 1:
                    name_part = parts[0].strip()
                    # 去掉时间信息
                    name_clean = re.sub(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', '', name_part).strip()
                    if name_clean and not name_clean.startswith('#E-s'):
                        agent_counter[name_clean] += 1
            
            # 标记新会话
            if not daily_data[current_date]['conv_started']:
                daily_data[current_date]['conv'] += 1
                daily_data[current_date]['conv_started'] = True
            
            continue
        
        # 内容行
        if line and not system_msg.match(line):
            msg = line.strip()
            if msg and last_speaker:
                # 过滤纯系统消息
                if msg.startswith('#E-s') or msg.startswith('~'):
                    continue
                
                current_conv.append({
                    'role': last_speaker,
                    'content': msg,
                    'date': current_date,
                })
                
                if current_date and current_date in daily_data:
                    if last_speaker == 'customer':
                        daily_data[current_date]['customer'] += 1
                    else:
                        daily_data[current_date]['agent'] += 1
                
                last_msg_had_time = False
    
    # 最后一个会话
    if current_conv and len(current_conv) >= 2:
        conversations.append(current_conv)
    
    # 按日期排序
    daily_stats = OrderedDict(sorted(daily_data.items()))
    
    # 关键词统计
    keyword_counts = Counter()
    for conv in conversations:
        for msg in conv:
            if msg['role'] == 'customer':
                for category, keywords in KEYWORD_CATEGORIES.items():
                    for kw in keywords:
                        if kw in msg['content']:
                            keyword_counts[kw] += 1
    
    # 负面对话样本
    negative_kws = set(NEGATIVE_WORDS)
    sample_negative = []
    for conv in conversations:
        has_negative = False
        customer_msgs = []
        for msg in conv:
            if msg['role'] == 'customer':
                customer_msgs.append(msg)
                for kw in negative_kws:
                    if kw in msg['content']:
                        has_negative = True
                        break
        if has_negative and len(sample_negative) < 50:
            sample_negative.append(conv)
    
    return {
        'conversations': conversations,
        'daily_stats': daily_stats,
        'keyword_counts': keyword_counts,
        'agent_counter': agent_counter,
        'sample_negative': sample_negative,
        'total_conversations': len(conversations),
    }


def get_summary_stats(parsed_data):
    """获取汇总统计"""
    convs = parsed_data['conversations']
    total_customer = sum(1 for c in convs for m in c if m['role'] == 'customer')
    total_agent = sum(1 for c in convs for m in c if m['role'] == 'agent')
    total_conv = parsed_data['total_conversations']
    num_agents = len(parsed_data['agent_counter'])
    
    dates = list(parsed_data['daily_stats'].keys())
    date_range = f"{dates[0]} ~ {dates[-1]}" if len(dates) >= 2 else "N/A"
    
    return {
        'total_conversations': total_conv,
        'total_customer_msgs': total_customer,
        'total_agent_msgs': total_agent,
        'num_agents': num_agents,
        'date_range': date_range,
    }
