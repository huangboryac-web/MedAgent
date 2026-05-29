# MedAgent - 个人医疗 AI 助手

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.50+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**MedAgent** 是一个基于 LangGraph 和 FastAPI 构建的专业个人医疗 AI 助手，提供症状分析、健康咨询、药物相互作用检查、多源知识检索等功能，同时具备严格的安全护栏和隐私保护机制。

## 核心特性

### 医疗专业能力
- **症状智能分析**：自动识别症状严重程度（轻度/中度/重度/危急）
- **意图路由系统**：区分医疗咨询/通用对话/紧急情况/澄清需求
- **多源知识检索**：整合向量数据库、学术文献、临床指南、权威医学网站
- **药物相互作用检查**：实时检查药物配伍禁忌和风险等级

### 安全与合规
- **四级安全护栏**：紧急症状检测、禁忌症检查、幻觉检测、自残/自杀意图识别
- **风险分级机制**：none/low/medium/high/critical 五级风险评估
- **医学免责声明**：自动添加免责声明，明确 AI 辅助性质
- **隐私保护**：本地部署优先，支持端到端加密会话

### 技术架构
- **LangGraph 状态图**：DAG 编排意图路由、症状分级、知识检索、交叉验证、反思循环
- **多 Skill 集成**：支持 deep-research, multi-search-engine, academic-search, summarize 等外部技能
- **RESTful API**：提供同步/异步/流式三种接口模式
- **Redis 会话管理**：支持多轮对话上下文和会话持久化

### 生产就绪
- **完整测试覆盖**：34+ 测试用例，100% 通过率
- **容器化部署**：Docker + Docker Compose 一键部署
- **监控告警**：Prometheus + Grafana 实时监控
- **性能优化**：异步处理、连接池、缓存策略

## 项目结构

```
MedAgent/
├── src/                    # 源代码目录
│   ├── agent/             # Agent 核心逻辑
│   │   ├── graph.py       # 基础 LangGraph 状态图
│   │   ├── enhanced_graph.py # 增强版（集成外部 Skill）
│   │   └── state.py       # Agent 状态定义
│   ├── api/               # API 接口层
│   │   └── routes/        # FastAPI 路由
│   │       ├── chat.py    # V1 基础聊天接口
│   │       └── enhanced_chat.py # V2 增强接口（认证+Skill）
│   ├── knowledge/         # 知识检索模块
│   │   ├── retriever.py   # 基础检索器
│   │   └── enhanced_retriever.py # 增强检索器（多源）
│   ├── skills/            # 外部 Skill 集成
│   │   ├── manager.py     # Skill 管理器
│   │   └── integration.py # Skill 集成服务
│   └── utils/             # 工具模块
│       ├── safety.py      # 安全护栏
│       ├── auth.py        # 用户认证
│       ├── conversation.py # 会话管理
│       ├── llm.py         # LLM 工厂
│       └── logger.py      # 日志系统
├── tests/                 # 测试目录
│   ├── test_agent.py      # Agent 测试
│   ├── test_app.py        # API 测试
│   ├── test_config.py     # 配置测试
│   └── test_phase3.py     # Phase 3 功能测试
├── config/                # 配置文件
│   └── .env.example       # 环境变量模板
├── docs/                  # 文档目录
│   ├── PRD.md            # 产品需求文档
│   ├── TASK_LOG.md       # 开发任务日志
│   ├── DEV_GUIDE.md      # 开发指南
│   ├── PHASE4_PLAN.md    # Phase 4 部署计划
│   └── GIT_WORKFLOW.md   # Git 工作流
└── requirements.txt       # Python 依赖
```

## 快速开始

### 环境准备

```bash
# 克隆项目
git clone https://github.com/DaemonOnCode/MedAgent.git
cd MedAgent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 到 `config/.env` 并填写必要的 API Key：

```bash
cp config/.env.example config/.env
```

编辑 `config/.env`：

```env
# LLM 配置
OPENAI_API_KEY=sk-...          # OpenAI API Key
ANTHROPIC_API_KEY=sk-ant-...   # Claude API Key
DEFAULT_LLM_PROVIDER=openai    # openai 或 anthropic
DEFAULT_LLM_MODEL=gpt-4o       # 模型名称

# 搜索配置
TAVILY_API_KEY=tvly-...        # Tavily 搜索 API Key

# 向量数据库（可选）
PINECONE_API_KEY=pc-...        # Pinecone API Key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=medagent

# Redis（会话持久化）
REDIS_URL=redis://localhost:6379/0

# 应用配置
APP_ENV=development            # development/production/test
APP_HOST=0.0.0.0
APP_PORT=8080
LOG_LEVEL=INFO
```

### 启动服务

```bash
# 启动开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

服务将在 `http://localhost:8080` 启动。

### 使用 API

#### 基础聊天接口（无需认证）

```bash
# 健康检查
curl http://localhost:8080/api/v1/health

# 发送消息
curl -X POST http://localhost:8080/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "最近有点头疼，应该怎么办？"}'
```

#### 增强接口（支持认证和外部 Skill）

```bash
# 需要 API Key 认证
curl -X POST http://localhost:8080/api/v2/chat/send \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "message": "高血压患者可以吃布洛芬吗？",
    "enable_skills": true,
    "enable_enhanced_search": true
  }'
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agent.py::TestAgentGraph -v
```

## API 文档

### 基础接口 (V1)

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v1/health` | GET | 健康检查 | 否 |
| `/api/v1/chat/send` | POST | 同步聊天 | 否 |
| `/api/v1/chat/stream` | POST | 流式聊天 | 否 |

### 增强接口 (V2)

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/v2/health` | GET | 增强健康检查 | 否 |
| `/api/v2/chat/send` | POST | 增强聊天（支持 Skill） | 是 |
| `/api/v2/drug/check` | POST | 药物相互作用检查 | 是 |
| `/api/v2/skills/list` | GET | 可用 Skill 列表 | 是 |

### 请求示例

```json
{
  "message": "症状描述或问题",
  "session_id": "可选会话ID",
  "enable_skills": true,
  "enable_enhanced_search": true,
  "user_context": {
    "age": 35,
    "gender": "male",
    "allergies": ["青霉素"],
    "chronic_conditions": ["高血压"]
  }
}
```

### 响应示例

```json
{
  "status": "success",
  "response": "已分析您的症状...",
  "intent": "medical",
  "symptom_severity": "mild",
  "risk_level": "none",
  "requires_disclaimer": true,
  "knowledge_sources": 3,
  "timestamp": "2026-05-29T15:30:00Z"
}
```

## 开发指南

### 添加新的 Skill

1. 在 `src/skills/manager.py` 中注册 Skill：

```python
SKILL_REGISTRY = {
    "new-skill": {
        "name": "New Skill",
        "description": "技能描述",
        "endpoint": "https://api.example.com/new-skill",
        "required_params": ["param1", "param2"],
        "category": "research",
    },
}
```

2. 在 `src/skills/integration.py` 中实现调用逻辑：

```python
async def call_new_skill(params: dict) -> dict:
    # 调用外部 API 或本地函数
    result = await external_api_call(params)
    return {"skill": "new-skill", "data": result}
```

3. 在 `src/knowledge/enhanced_retriever.py` 中集成到检索流程。

### 扩展安全规则

编辑 `src/utils/safety.py`：

```python
# 添加新的风险检测规则
class SafetyGuardrail:
    def assess_message(self, user_message: str) -> RiskAssessment:
        # 现有检测...
        
        # 添加新规则
        if self._detect_new_risk(user_message):
            risk.risk_level = "medium"
            risk.warnings.append("新的风险警告")
            
        return risk
```

## Docker 部署

### 使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 单独运行

```bash
# 构建镜像
docker build -t medagent:latest .

# 运行容器
docker run -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -e APP_ENV=production \
  medagent:latest
```

## 监控与告警

### Prometheus 指标

- `medagent_api_requests_total` - API 请求总数
- `medagent_api_duration_seconds` - 请求耗时
- `medagent_llm_calls_total` - LLM 调用次数
- `medagent_redis_connections` - Redis 连接数
- `medagent_risk_levels_total` - 风险等级分布

### Grafana 仪表板

预置仪表板包含：
- API 性能监控
- LLM 使用统计
- 安全事件分析
- 系统资源监控

## 测试策略

### 单元测试
```bash
pytest tests/ -v --tb=short
```

### 集成测试
```bash
pytest tests/test_phase3.py -v
```

### 端到端测试
```bash
python scripts/e2e_test.py
```

### 性能测试
```bash
locust -f scripts/locustfile.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

请遵循 [开发指南](docs/DEV_GUIDE.md) 和 [Git 工作流](docs/GIT_WORKFLOW.md)。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 免责声明

**重要提示**：MedAgent 是 AI 辅助工具，不提供医疗诊断、治疗建议或替代专业医疗意见。所有内容仅供参考，不能替代执业医师的专业判断。如有医疗需求，请咨询合格医疗专业人员。

## 支持与反馈

- 问题报告: [GitHub Issues](https://github.com/DaemonOnCode/MedAgent/issues)
- 功能建议: [GitHub Discussions](https://github.com/DaemonOnCode/MedAgent/discussions)

---

**MedAgent** - 让 AI 成为您的健康助手，而非医生替代者。
