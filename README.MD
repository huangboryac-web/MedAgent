# MedAgent API Edition

> 基于API调用的专业医疗AI助手 - MedAgent改造版

## 项目简介

MedAgent API Edition 是一个全API调用的专业医疗AI助手系统，采用LangGraph智能体编排架构，集成多个专业Skill，为用户提供安全、可靠、专业的健康咨询服务。

## 核心特性

- **智能体编排**：基于LangGraph的状态图管理，支持意图路由、多轮对话、反思循环
- **多源知识检索**：同时调用多个搜索引擎和学术数据库，交叉验证确保准确性
- **多Skill协作**：集成deep-research、multi-search-engine、academic-search等专业能力
- **安全防护**：高危症状识别、用药禁忌检查、幻觉检测、自动免责声明
- **全API调用**：无需本地部署模型，灵活可扩展

## 技术栈

| 组件    | 技术                  |
| ----- | ------------------- |
| 后端框架  | FastAPI             |
| 智能体编排 | LangGraph           |
| 大模型   | GPT-4o / Claude API |
| 向量数据库 | Pinecone / Weaviate |
| 缓存    | Redis               |
| 数据库   | PostgreSQL          |

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url> medagent-api
cd medagent-api

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入API密钥

# 5. 运行
uvicorn src.main:app --reload
```

## 项目结构

```
health/
├── docs/               # 项目文档
│   ├── PRD.md          # 产品需求文档
│   ├── TASK_LOG.md     # 任务日志
│   ├── DEV_GUIDE.md    # 开发手册
│   └── GIT_WORKFLOW.md # Git工作流规范
├── src/                # 源代码
│   ├── agent/          # LangGraph智能体编排
│   ├── api/            # FastAPI接口层
│   ├── knowledge/      # 知识检索系统
│   ├── skills/         # Skill集成层
│   └── utils/          # 工具模块
├── tests/              # 测试代码
├── config/             # 配置文件
├── .gitignore
└── README.md
```

## 文档

- [产品需求文档 (PRD)](docs/PRD.md)
- [任务日志](docs/TASK_LOG.md)
- [开发手册](docs/DEV_GUIDE.md)
- [Git工作流规范](docs/GIT_WORKFLOW.md)

## 开发计划

1. **Phase 1**：基础框架搭建 (1-2周)
2. **Phase 2**：核心功能开发 (2-3周)
3. **Phase 3**：Skill集成与增强 (1-2周)
4. **Phase 4**：测试与优化 (1-2周)

## 贡献指南

1. 从 `develop` 分支创建功能分支
2. 遵循[开发手册](docs/DEV_GUIDE.md)中的代码规范
3. 提交Pull Request到 `develop`
4. 通过Code Review后合并

## 安全声明

本项目为健康咨询辅助工具，**不替代专业医疗诊断**。如遇紧急症状，请立即就医。

## 许可证

MIT License
