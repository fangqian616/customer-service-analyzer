[English](README_EN.md) | 中文

# 客服舆情分析系统

上传飞书导出的客服聊天记录，一键生成数据可视化报告 + AI深度分析。

## 功能

- 自动解析聊天记录（飞书导出格式）
- 13类咨询场景自动分类排名
- 关键词频次统计与情感分类
- 负面情绪深度分析 + 对话样本
- 每日趋势、售前售后对比
- 一键导出PDF报告（7页图表）
- 可选接入DeepSeek AI生成深度分析文本（追加到PDF末尾）

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 使用

1. 打开浏览器访问 Streamlit 页面
2. 上传聊天记录文件（.log / .txt）
3. 查看交互式图表
4. 切到「导出报告」Tab 下载PDF

## 可选：AI分析

在侧边栏填入 DeepSeek API Key，即可在导出时选择"完整报告"，自动调用AI生成8模块深度分析文本。

## 文件说明

- `app.py` — Streamlit Web界面
- `parser.py` — 聊天记录解析引擎
- `visualizer.py` — 图表与PDF生成引擎
- `requirements.txt` — 依赖清单
