# Harvey LAB (Legal Agent Benchmark) 测试

本目录把 Harvey 开源的 **Legal Agent Benchmark (LAB)**（[harveyai/harvey-labs](https://github.com/harveyai/harvey-labs)）接入本仓库，用于在真实法律工作任务上评测 LLM agent。

## LAB 是什么

- **任务集**：2,010 个任务，覆盖 27 个执业领域（并购、诉讼、税务、知识产权、破产重组……），工作类型包括 analyze / draft / review / extract / research。
- **每个任务**包含：给 agent 的指令、一个模拟客户案卷（`documents/`，docx/xlsx/pdf 等）、要求产出的交付物（如 `red-flag-memo.docx`），以及专家撰写的逐条 pass/fail 评分标准（rubric）。
- **执行环境**：agent 在一个断网的 podman 容器里工作，只有 7 个工具：`bash`、`read`、`write`、`edit`、`glob`、`grep`、`finish`。
- **评分**：用 LLM 当裁判，标准配置是 Claude Sonnet 4.6 + GPT-5.5 两个裁判。主指标是 **all-pass**：只有所有标准全部通过，这个任务才算 1 分，否则为 0。criterion pass rate（标准通过率）作为辅助诊断。

## 目录

| 文件 | 作用 |
|---|---|
| `setup.sh` | 克隆固定版本的 harvey-labs（默认 `v1.2.0`）到 `vendor/`，安装依赖、pandoc ≥ 3.5、podman，并准备沙箱镜像 |
| `sandbox/Dockerfile.ubuntu` | 备用沙箱镜像。当 ghcr.io 和 deb.debian.org 都访问不到时使用（例如 Claude Code 云端环境），工具集与上游一致 |
| `smoke_test.py` / `run_smoke_test.sh` | **不需要 API key** 的端到端连通性测试：用脚本化的假模型走完真实的 harness → 沙箱 → 交付物 → 评分器文档提取全链路 |
| `run_task.sh` | 跑单个任务：agent 运行 → rubric 评分 → HTML 报告 |
| `vendor/` | 上游 checkout 和运行结果（约 4 GB），已加入 `.gitignore` |

## 快速开始

```bash
# 1. 环境（首次需要几分钟，克隆约 4 GB）
harvey_lab/setup.sh

# 2. 不花钱的连通性检查
harvey_lab/run_smoke_test.sh

# 3. 配置 API key：标准双裁判评分需要 Anthropic 和 OpenAI 两个 key
cat > harvey_lab/vendor/harvey-labs/.env <<'EOF'
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_API_KEY=...        # 只有评测 Gemini 时才需要
EOF

# 4. 跑一个任务（官方教程任务：并购尽调 red flag 审查，13 份文件，50 条标准）
harvey_lab/run_task.sh anthropic/claude-sonnet-4-6 corporate-ma/review-data-room-red-flag-review
```

### 会话模式：用 Claude Code 自身额度跑，不需要 API key

`session_runner.py` 把官方流程中调用 API 的两处换成了 Claude Code 子 agent。沙箱、system prompt、skill 手册、评分标准、评分代码和报告生成都沿用官方代码：

1. `harvey_lab/session.sh prepare-agent <task>`：启动官方 podman 沙箱。沙箱断网，`documents/` 以只读方式挂载，容器里看不到 `task.json`。同时生成 `AGENT_BRIEF.md`，内容是官方 system prompt、skill 手册和任务指令。
2. **agent 子 agent** 读这份 brief，所有命令都通过 `harvey_lab/sbx.sh <run_dir> '<cmd>'` 在沙箱里执行。每条命令都会记到 `commands.jsonl`，交付物写进 `/workspace/output`。
3. `harvey_lab/session.sh finish-agent <run_id>`：关闭容器，写入 `config.json` 和 `metrics.json`。文档覆盖率根据命令日志统计；token 数在会话模式下拿不到，记为 0。
4. `harvey_lab/session.sh prepare-judge <run_id> <task>`：用官方 `score_rubric()` 记录每条标准本该发给裁判的交付物文本，生成 `judge/bundle.md`。
5. **judge 子 agent**（和 agent 不是同一个，互相独立）逐条按官方 `rubric_criterion` prompt 判 pass/fail，结果写到 `judge/responses.json`。
6. `harvey_lab/session.sh finalize <run_id> <task>`：用官方 `evaluate_run()` 写出 `scores.json`，再生成 `report.html`。

这种模式下，裁判是本会话的 Claude，不是标准的 Sonnet 4.6 + GPT-5.5 双裁判，所以分数标记为 `claude-code-session-judge`，**不能和官方公布的分数直接比较**，只适合内部对比和找问题。

### 浏览任务

```bash
cd harvey_lab/vendor/harvey-labs
uv run python -m lab_core.utils.list_tasks --area litigation-dispute-resolution
uv run python -m lab_core.utils.list_tasks --work-type draft
uv run python -m lab_core.utils.describe_task corporate-ma/review-data-room-red-flag-review
```

### 批量跑（sweep）与对比

```bash
cd harvey_lab/vendor/harvey-labs
# 先 dry-run，确认要跑哪些组合
uv run python -m lab_core.utils.sweep --task corporate-ma --models sonnet --reasoning high --dry-run
uv run python -m lab_core.utils.sweep --task corporate-ma --models sonnet --reasoning high --parallel 4
# 生成对比面板
uv run python -m lab_core.evaluation.compare --area corporate-ma
```

`--task` 可以填单个任务、一个领域，或者 `all`。

## 测试记录

**2026-10-15**，harvey-labs `v1.2.0`，Claude Code 云端环境（Linux，rootless podman，备用 Ubuntu 沙箱镜像）

| 检查项 | 结果 |
|---|---|
| 上游单元测试 `uv run pytest` | 12,906 passed，62 skipped |
| 任务索引 `list_tasks` | 2,010 个任务，27 个领域，全部可加载 |
| sweep `--dry-run`（教程任务 × sonnet） | 规划正常 |
| 冒烟测试 `corporate-ma/review-data-room-red-flag-review` | PASSED：读取 13/13 份文件，生成 `red-flag-memo.docx` 和 `red-flag-tracker.xlsx`，评分器能匹配并提取这两个文件 |
| 冒烟测试 `real-estate/extract-psa-key-terms/scenario-01`（嵌套 scenario） | PASSED：读取 3/3 份文件，`psa-term-sheet.docx` 可提取 |
| 真实模型运行 + LLM 裁判评分 | **未运行**：环境里没有 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`。`run_eval` 在创建裁判客户端时报缺 key 并停止，这是预期行为 |

配置好 key 以后，执行 `run_task.sh` 就能出第一份真实分数。

### 会话模式结果（Claude Code 子 agent 做任务，另一个独立子 agent 当裁判）

| 任务 | 标准通过 | all-pass | 文档覆盖 | 用时 | 结果目录 |
|---|---|---|---|---|---|
| `corporate-ma/review-data-room-red-flag-review` | **45/50（90%）** | 0（FAIL） | 13/13 | agent 约 20 分钟，sandbox 命令 53 条 | `session_results/corporate-ma/review-data-room-red-flag-review/claude-code-session/20261015-065804/` |

没有通过的 5 条标准：

- C-030：接受了 $1.8M 石棉清理的 add-back，没有质疑它是否真的是一次性项目
- C-032：把 Wyoming 许可证到期这个干扰项列成了 HIGH 风险
- C-041：缺少“看似有问题、实际已排除”的事项清单
- C-045：没有提到 2025-01-24 的投资委员会会议
- C-046：漏了 Consolidated Mining 占 11.4%（$14.5M）和 DOE 的 $24.4M

另外，裁判标出了 5 条判得偏宽松的通过项（C-010、C-011、C-016、C-047、C-050）。按最严格的读法，这几条也可能判为不通过。

### 批量测评（2026-10-15，26 个任务）

每个执业领域抽 1 个任务（固定随机种子，见 `batch_tasks.json`），加上前面的并购任务，共 26 个。尽调（diligence）领域没有纳入：它的每个任务都有 2,600–4,000 份文件、400–1,100 条标准，规模太大。

| 指标 | 结果 |
|---|---|
| all-pass（全部标准通过） | **3 / 26**：反垄断、银行融资、劳动雇佣 |
| 标准通过率（合并计算） | **92.7%**（1,221 / 1,317 条） |
| 通过率 ≥ 95% 的任务 | 12 / 26 |
| 隔离审计 | 26 / 26 干净（做题和判卷两边都审计了） |
| 双裁判一致性（8 个任务复判） | 452 / 455 条一致（99.3%）；all-pass 结论 7 / 8 一致 |

96 条未通过标准的人工归类：

| 类别 | 条数 |
|---|---|
| 漏掉具体问题或分析角度 | 36 |
| 疑似标准本身可商榷 | 18（其中 13 条在税务任务） |
| 立场与专家预期不同 | 15 |
| 没量化或没给市场基准 | 14 |
| 轻重判断不同 | 7 |
| 结构或格式要求 | 6 |

- 可视化总览：`session_results/overview.html`
- 汇总数据：`session_results/summary.json`
- 各任务的交付物、分数、审计结果：`session_results/<run_id>/`

相关脚本：

| 脚本 | 作用 |
|---|---|
| `batch.py` | 批量调度 |
| `audit_transcript.py` | 审计子 agent 的工具调用记录 |
| `rejudge.py` | 第二裁判复判与一致性统计 |
| `build_summary.py`、`build_page.py` | 生成汇总数据和总览页 |

## 注意事项

- **成本**：一个任务一般要几十万输入 token，再加上每条标准 × 2 个裁判的评分调用。跑全量 2,010 个任务之前，先用 `--dry-run` 估算规模。
- **可比性**：只有在相同的 harvey-labs commit 上、用标准裁判对产生的分数才能直接比较。换版本时，先看上游的 `CHANGELOG.md`。用 `JUDGES=...` 换裁判后，结果标记为 `custom-dual`/单裁判，不能和官方分数比。
- **备用镜像**：`Dockerfile.ubuntu` 换了基础镜像（Ubuntu 24.04 替代 Debian slim），工具和 Python 包与上游一致。正式出分时，建议能拉到上游镜像就用上游镜像。
- 任务文档是在律师指导下批量合成的，不是真实案卷。
