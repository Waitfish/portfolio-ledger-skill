# portfolio-ledger-skill

[![CI](https://github.com/Waitfish/portfolio-ledger-skill/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Waitfish/portfolio-ledger-skill/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Release](https://img.shields.io/github/v/release/Waitfish/portfolio-ledger-skill)](https://github.com/Waitfish/portfolio-ledger-skill/releases)

一个给 Hermes 使用的本地股票账本技能，用来把结构化的持仓和交易记录写入本地 SQLite。

英文说明见：`README.en.md`

## 这个项目解决什么问题

这个 skill 不负责解析截图。

它的定位很明确：

1. Hermes 或其他大模型先把截图、PDF、表格、自然语言整理成结构化 JSON
2. 这个 skill 负责校验 JSON
3. 这个 skill 负责把数据写入本地 SQLite

也就是说，它是一个“本地股票账本接口层”，不是 OCR 工具。

## 功能

1. `replace_positions`
2. `append_trades`
3. `get_positions`
4. `get_trades`
5. `get_import_batch`
6. `manifest`

## 目录结构

```text
.
├── SKILL.md
├── skill.py
├── portfolio_ledger/
│   ├── normalize.py
│   ├── schemas.py
│   ├── storage.py
│   └── db/init.sql
├── examples/
└── tests/
```

## 环境要求

- Python 3.11+
- 不依赖第三方 Python 包

## 本地直接运行

### 查看 manifest

```bash
python3 skill.py manifest
```

### 写入一份持仓快照

```bash
python3 skill.py < examples/tool_replace_positions.json
```

### 追加交易记录

```bash
python3 skill.py < examples/tool_append_trades.json
```

### 查询当前持仓

```bash
printf '%s' '{"tool":"get_positions","input":{"portfolio_id":"main"}}' | python3 skill.py
```

## 数据库路径

默认会写到：

```text
data/portfolio.db
```

也可以通过环境变量覆盖：

```bash
PORTFOLIO_LEDGER_DB=/tmp/portfolio.db python3 skill.py manifest
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 在 Hermes 中安装

先把这个仓库加成 Hermes 的 skill source：

```bash
hermes skills tap add Waitfish/portfolio-ledger-skill
```

再安装 skill：

```bash
hermes skills install Waitfish/portfolio-ledger-skill/portfolio-ledger
```

如果 Hermes 要你指定分类，可以用：

```bash
hermes skills install Waitfish/portfolio-ledger-skill/portfolio-ledger --category productivity
```

检查是否安装成功：

```bash
hermes skills list | grep portfolio-ledger
```

### 一键安装脚本

如果你已经把仓库 clone 到本地，可以直接运行：

```bash
bash install.sh
```

这个脚本会把 `SKILL.md` 安装到：

```text
~/.hermes/skills/productivity/portfolio-ledger/
```

注意：

1. 这个脚本安装的是 Hermes 的 skill 提示词
2. Python 实现仍然来自你当前 clone 下来的仓库目录
3. 所以推荐在这个仓库目录内使用 Hermes

## 在 Hermes 中使用

启动一个带这个 skill 的 Hermes 会话：

```bash
hermes chat -s portfolio-ledger
```

### 示例：保存持仓

```text
Use the portfolio-ledger skill to save a full positions snapshot for portfolio_id main at 2026-04-22T15:30:00+08:00 with one holding: AAPL quantity 10, avg_cost 100, market US, cost_currency USD.
```

### 示例：查询当前持仓

```text
Use the portfolio-ledger skill to query current positions for portfolio_id main and return the JSON result.
```

### 示例：追加交易

```text
Use the portfolio-ledger skill to append one trade for portfolio_id main: trade_time 2026-04-23T09:35:22+08:00, symbol AAPL, side BUY, quantity 2, price 100, amount 200.
```

### 示例：查询交易

```text
Use the portfolio-ledger skill to query trades for portfolio_id main.
```

## 推荐自测流程

建议按这个顺序测一轮：

1. `python3 skill.py manifest`
2. `python3 skill.py < examples/tool_replace_positions.json`
3. `python3 skill.py < examples/tool_append_trades.json`
4. `python3 -m unittest discover -s tests -v`
5. `hermes chat -s portfolio-ledger`

## 发布版本

你可以在 GitHub Releases 页面获取当前发布版本：

```text
https://github.com/Waitfish/portfolio-ledger-skill/releases
```

## 说明

这个 skill 的设计目标是：

1. 显式 API
2. 本地 SQLite 落库
3. 持仓快照和交易流水分离
4. 所有写入都有批次记录，方便追踪和排错

如果你要把截图直接接进来，应该让上游模型先把截图转成结构化 JSON，再调用这个 skill。
