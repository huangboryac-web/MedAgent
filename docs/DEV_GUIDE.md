# 开发手册与准则 (Development Guide)

## 1. 代码规范

### 1.1 Python代码规范

- **格式工具**：Black (line-length=100)
- **代码检查**：Ruff (替代Flake8+isort)
- **类型检查**：mypy (strict mode)
- **文档字符串**：Google Style Docstring

```python
# 示例：函数定义规范
def analyze_symptom(
    symptoms: list[str],
    duration: str,
    severity: int,
    user_context: dict[str, Any] | None = None
) -> SymptomAnalysis:
    """分析用户症状并返回初步评估结果。

    Args:
        symptoms: 用户描述的症状列表
        duration: 症状持续时间描述
        severity: 严重程度，1-5级
        user_context: 用户健康档案上下文，可选

    Returns:
        症状分析结果对象

    Raises:
        InvalidSymptomError: 当症状描述无效时
        HighRiskSymptomError: 当检测到高危症状时
    """
    ...
```

### 1.2 命名规范

- **模块名**：小写+下划线 (`symptom_analyzer.py`)
- **类名**：大驼峰 (`SymptomAnalyzer`)
- **函数名**：小写+下划线 (`analyze_symptom`)
- **常量**：大写+下划线 (`MAX_RETRY_COUNT`)
- **私有属性**：前缀下划线 (`_cache`)

### 1.3 项目结构规范

```
src/
├── agent/          # LangGraph智能体编排
│   ├── graph.py    # 状态图定义
│   ├── nodes.py    # 节点实现
│   └── state.py    # 状态模型
├── api/            # FastAPI接口层
│   ├── routes/     # 路由模块
│   ├── schemas/    # Pydantic模型
│   └── middleware/ # 中间件
├── knowledge/      # 知识检索系统
│   ├── search/     # 搜索引擎
│   ├── retrieval/  # 向量检索
│   └── fusion/     # 结果融合
├── skills/         # Skill集成层
│   ├── deep_research.py
│   ├── multi_search.py
│   └── academic.py
├── utils/          # 工具模块
│   ├── safety.py   # 安全防护
│   ├── logger.py   # 日志
│   └── config.py   # 配置
└── main.py         # 应用入口
```

---

## 2. Git规范

### 2.1 分支策略

- **主分支**：
  
  - `main` - 生产环境代码（只接受merge，禁止直接commit）
  - `develop` - 开发主分支（日常开发合并目标）

- **功能分支**：
  
  - `feature/<module-name>` - 新功能开发
  - `bugfix/<issue-id>` - Bug修复
  - `hotfix/<issue-id>` - 紧急修复（基于main分支）
  - `refactor/<module-name>` - 代码重构

- **提交信息格式**：
  
  ```
  <type>(<scope>): <subject>
  
  <body>
  
  <footer>
  ```
  
  类型：`feat` `fix` `docs` `style` `refactor` `test` `chore`
  
  示例：
  
  ```
  feat(agent): 添加症状分析节点
  fix(safety): 修复高危症状识别误报
  docs(prd): 更新PRD功能需求章节
  ```

### 2.2 分支命名规则

- 功能分支：`feature/PH1-001-symptom-analyzer`
- 修复分支：`bugfix/issue-42-fix-hallucination`
- 紧急修复：`hotfix/critical-safety-bug`

### 2.3 工作流程

1. 从`develop`创建功能分支
2. 在功能分支上开发和自测
3. 提交Pull Request到`develop`
4. Code Review通过后合并
5. 定期将`develop`合并到`main`发布版本

### 2.4 合并策略

- **功能分支→develop**：Squash Merge（压缩提交记录）
- **develop→main**：Merge Commit（保留完整历史）
- **hotfix→main**：Merge Commit

### 2.5 禁止事项

- ❌ 直接push到`main`或`develop`
- ❌ 提交包含密钥/Token的代码
- ❌ 提交大文件（>10MB），使用Git LFS
- ❌ Force push到共享分支
- ❌ 合并未通过CI的分支

---

## 3. 架构设计准则

### 3.1 设计原则

1. **单一职责**：每个模块只负责一个功能领域
2. **开闭原则**：对扩展开放，对修改关闭
3. **依赖倒置**：依赖抽象接口，不依赖具体实现
4. **接口隔离**：不强迫依赖不需要的接口

### 3.2 LangGraph状态图设计准则

- **状态定义**：使用TypedDict或Pydantic模型
- **节点设计**：每个节点独立可测试
- **边定义**：条件边使用明确的路由函数
- **错误处理**：每个节点内部处理异常，避免图崩溃

```python
# 状态图设计示例
class AgentState(TypedDict):
    """Agent全局状态"""
    messages: list[Message]          # 对话历史
    intent: str                      # 用户意图
    risk_level: str                  # 风险等级
    search_results: list[SearchResult]  # 检索结果
    verified: bool                   # 是否经过验证
    final_response: str              # 最终回复

# 图构建
workflow = StateGraph(AgentState)
workflow.add_node("intent_router", route_intent)
workflow.add_node("symptom_check", check_symptoms)
workflow.add_node("knowledge_search", search_knowledge)
workflow.add_node("response_generate", generate_response)
workflow.add_node("safety_guardrail", apply_guardrail)

workflow.set_entry_point("intent_router")
workflow.add_conditional_edges("intent_router", route_by_intent, {...})
...
```

### 3.3 API设计准则

- **RESTful设计**：资源命名使用名词复数
- **版本管理**：URL路径版本 (`/api/v1/...`)
- **错误处理**：统一错误响应格式
- **认证鉴权**：API Key + JWT双认证

```json
// 统一错误响应格式
{
  "error": {
    "code": "SYMPTOM_INVALID",
    "message": "症状描述无效",
    "details": {"field": "symptoms", "reason": "empty list"},
    "timestamp": "2026-05-29T14:30:00Z"
  }
}
```

---

## 4. 安全开发准则

### 4.1 API密钥管理

- ✅ 所有密钥存储在`.env`文件（不提交到Git）
- ✅ 使用环境变量注入，禁止硬编码
- ✅ 定期轮换API密钥
- ✅ 使用Secret Manager（生产环境）

### 4.2 医疗安全准则

1. **免责声明**：每次回复必须包含医疗免责声明
2. **高危拦截**：识别到高危症状时，不提供建议，立即建议就医
3. **拒绝处方**：禁止生成具体的处方和剂量建议
4. **证据标注**：所有健康建议标注信息来源和证据等级

### 4.3 数据安全

- **传输加密**：HTTPS
- **存储加密**：数据库加密
- **日志脱敏**：不记录用户详细健康信息
- **数据删除**：支持用户请求删除所有数据

### 4.4 幻觉防止

- **交叉验证**：多源信息对比
- **置信度标注**：每个回答标注置信度
- **来源追溯**：所有信息可追溯到原始来源
- **自我审查**：生成后自动检查事实一致性

---

## 5. 测试准则

### 5.1 测试层次

- **单元测试** (pytest)：覆盖所有模块函数
- **集成测试**：测试API接口和模块交互
- **E2E测试**：测试完整用户流程
- **安全测试**：测试安全防护机制

### 5.2 测试覆盖率目标

| 模块         | 覆盖率目标 |
| ---------- | ----- |
| agent/     | ≥ 90% |
| api/       | ≥ 85% |
| knowledge/ | ≥ 85% |
| skills/    | ≥ 80% |
| utils/     | ≥ 90% |

### 5.3 关键测试用例

```python
# 示例：症状分析测试
def test_high_risk_symptom_detection():
    """测试高危症状必须触发就医建议"""
    result = symptom_checker.check(["剧烈胸痛", "呼吸困难"])
    assert result.risk_level == "HIGH"
    assert result.action == "SEEK_EMERGENCY"

def test_safety_guardrail_block_prescription():
    """测试安全护栏拦截处方生成"""
    with pytest.raises(SafetyViolationError):
        safety_guard.check("请给我开阿莫西林500mg每日三次")
```

---

## 6. 决策日志 (ADR)

### 6.1 已批准决策

| 编号      | 日期         | 决策                      | 理由                 | 影响   |
| ------- | ---------- | ----------------------- | ------------------ | ---- |
| ADR-001 | 2026-05-29 | 采用LangGraph替代纯LangChain | 状态图管理更直观，支持循环和条件回退 | 架构核心 |
| ADR-002 | 2026-05-29 | 全API调用模式                | 放弃本地部署，提升专业性和灵活性   | 架构核心 |
| ADR-003 | 2026-05-29 | 多Skill并行执行优先于串行         | 响应更快，信息更全面         | 性能优化 |
| ADR-004 | 2026-05-29 | 采用FastAPI框架             | 异步性能好，生态完善         | 技术选型 |

### 6.2 待讨论决策

| 编号      | 议题      | 选项                   | 阻塞原因      |
| ------- | ------- | -------------------- | --------- |
| ADR-005 | 前端框架选择  | React vs Vue vs 纯API | 待确认是否需要前端 |
| ADR-006 | 向量数据库选择 | Pinecone vs Weaviate | 待评估成本和性能  |
| ADR-007 | 大模型选择   | GPT-4o vs Claude 3.5 | 待测试医疗场景表现 |

---

## 7. 发布流程

### 7.1 版本号规范 (SemVer)

- `MAJOR.MINOR.PATCH` (例如：1.2.3)
- MAJOR：不兼容的API变更
- MINOR：向后兼容的功能新增
- PATCH：向后兼容的Bug修复

### 7.2 发布检查清单

- [ ] 所有测试通过
- [ ] 代码审查通过
- [ ] 文档更新完成
- [ ] 变更日志更新
- [ ] 安全扫描通过
- [ ] 性能测试通过

---

**版本历史**
| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2026-05-29 | 初始版本 |
| | | |