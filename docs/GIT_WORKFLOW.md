# Git工作流程规范

## 1. Git初始化

### 1.1 仓库创建

```bash
cd C:\Users\22334\Downloads\health
git init
git checkout -b main
```

### 1.2 .gitignore 配置

项目根目录必须包含`.gitignore`文件，内容见下方。

### 1.3 初始提交

```bash
git add .
git commit -m "chore: 初始化项目结构和文档"
git branch develop
git branch feature/PH1-001-project-init
```

---

## 2. 分支策略详细说明

```
main (生产)
  │
  ├── develop (开发主线)
  │     │
  │     ├── feature/PH1-001-project-init        (项目初始化)
  │     ├── feature/PH1-101-fastapi-framework    (API框架)
  │     ├── feature/PH2-001-langgraph-agent      (智能体编排)
  │     ├── feature/PH2-101-multi-search         (多搜索引擎)
  │     ├── bugfix/issue-42-fix-hallucination    (Bug修复)
  │     └── refactor/PH3-001-optimize-retrieval  (重构)
  │
  ├── hotfix/critical-safety-fix (紧急修复)
  │
  └── release/v1.0.0 (发布分支)
```

## 3. 开发流程

### 3.1 新功能开发流程

```bash
# 1. 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/PH2-001-langgraph-agent

# 2. 开发，频繁提交
git add src/agent/graph.py
git commit -m "feat(agent): 创建LangGraph状态图基础结构"

# 3. 推送分支
git push origin feature/PH2-001-langgraph-agent

# 4. 创建Pull Request到develop
# 在GitHub上创建PR，添加描述和关联任务

# 5. Code Review通过后合并
# 使用Squash Merge
```

### 3.2 Bug修复流程

```bash
# 1. 从develop创建修复分支
git checkout develop
git checkout -b bugfix/issue-42-fix-hallucination

# 2. 修复并提交
git add src/utils/safety.py
git commit -m "fix(safety): 修复幻觉检测误报 #42"

# 3. 推送到远程
git push origin bugfix/issue-42-fix-hallucination

# 4. 创建PR，关联Issue #42
```

### 3.3 紧急修复流程

```bash
# 1. 从main创建hotfix分支
git checkout main
git checkout -b hotfix/critical-safety-fix

# 2. 修复并提交
git add src/utils/safety.py
git commit -m "hotfix(safety): 修复紧急安全漏洞"

# 3. 合并到main和develop
git checkout main
git merge hotfix/critical-safety-fix
git checkout develop
git merge hotfix/critical-safety-fix

# 4. 删除hotfix分支
git branch -d hotfix/critical-safety-fix
```

---

## 4. 提交规范

### 4.1 提交信息模板

```
<type>(<scope>): <subject>
<空行>
<body>
<空行>
<footer>
```

### 4.2 类型定义

| 类型       | 说明    | 示例                          |
| -------- | ----- | --------------------------- |
| feat     | 新功能   | feat(agent): 添加症状分析节点       |
| fix      | Bug修复 | fix(safety): 修复高危症状误报       |
| docs     | 文档更新  | docs(prd): 更新功能需求           |
| style    | 代码格式  | style(agent): 统一导入格式        |
| refactor | 重构    | refactor(knowledge): 重构检索管道 |
| test     | 测试    | test(api): 添加症状分析测试         |
| chore    | 构建/工具 | chore(deps): 更新依赖版本         |
| perf     | 性能优化  | perf(search): 优化检索延迟        |

### 4.3 提交频率要求

- **最少**：每天至少提交一次（有代码变更时）
- **最多**：每个功能点一次提交（通过Squash合并规范）

---

## 5. 代码审查流程

### 5.1 PR模板

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 重构
- [ ] 文档更新

## 关联任务
PH2-001 (智能体编排开发)

## 变更说明
添加了LangGraph状态图基础结构，包括：
- 状态定义(AgentState)
- 意图路由节点
- 条件边逻辑

## 测试计划
- [x] 单元测试通过
- [x] 集成测试通过
- [ ] 性能测试（待完成）

## 截图/示例
（如有）

## 检查清单
- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 没有引入安全问题
```

### 5.2 审查要点

- [ ] 代码逻辑正确性
- [ ] 边界条件处理
- [ ] 错误处理完善
- [ ] 安全性检查
- [ ] 性能影响评估
- [ ] 测试覆盖充分
- [ ] 文档更新同步

---

## 6. .gitignore配置

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
.eggs/

# 虚拟环境
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 环境变量
.env
.env.local
.env.*.local

# API密钥
*.key
*.pem
secrets/
credentials/

# 日志
*.log
logs/

# 数据库
*.db
*.sqlite
*.sqlite3

# 缓存
.cache/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# 临时文件
temp/
tmp/
*.tmp

# 大文件
*.gguf
*.bin
*.safetensors
*.pkl

# OS
.DS_Store
Thumbs.db

# Docker
.docker/

# 测试覆盖
htmlcov/
.coverage
coverage.xml

# Jupyter
.ipynb_checkpoints/
*.ipynb
```

---

## 7. 常用Git命令速查

### 7.1 分支操作

```bash
# 查看所有分支
git branch -a

# 切换分支
git checkout <branch-name>

# 创建并切换分支
git checkout -b <branch-name>

# 删除本地分支
git branch -d <branch-name>

# 删除远程分支
git push origin --delete <branch-name>
```

### 7.2 提交相关

```bash
# 查看状态
git status

# 查看差异
git diff

# 暂存所有变更
git add .

# 提交
git commit -m "type(scope): description"

# 修改最后一次提交
git commit --amend

# 撤销未暂存的变更
git checkout -- <file>

# 撤销已暂存的变更
git reset HEAD <file>
```

### 7.3 合并与变基

```bash
# 合并分支
git merge <branch-name>

# 变基（保持线性历史）
git rebase develop

# 交互式变基（合并提交）
git rebase -i HEAD~3

# 终止合并/变基
git merge --abort
git rebase --abort
```

### 7.4 远程操作

```bash
# 添加远程仓库
git remote add origin <url>

# 查看远程仓库
git remote -v

# 拉取代码
git fetch origin
git pull origin develop

# 推送代码
git push origin <branch-name>

# 强制推送（谨慎使用！）
git push --force-with-lease origin <branch-name>
```

### 7.5 暂存与恢复

```bash
# 暂存当前工作
git stash

# 查看暂存列表
git stash list

# 恢复最近暂存
git stash pop

# 恢复指定暂存
git stash apply stash@{0}
```

---

## 8. CI/CD集成（后续实现）

### 8.1 GitHub Actions工作流

```yaml
name: CI
on:
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint code
        run: |
          pip install ruff
          ruff check src/
```

### 8.2 提交前检查 (pre-commit hooks)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

---

**版本历史**
| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2026-05-29 | 初始版本，完整Git工作流规范 |
| | | |