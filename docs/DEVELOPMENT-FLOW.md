# Development Flow

## 1. 开发原则

项目后续开发遵循以下顺序：

- 先定抽象
- 再定接口
- 再做数据与任务模型
- 再做服务实现
- 最后接入聊天入口和页面

也就是说，当前阶段不直接从聊天交互细节开写，而是先把服务边界和领域模型稳定下来。

## 2. 推荐开发阶段

### Phase 0：文档与边界确认

目标：

- 明确方案 A 为最终架构
- 明确 `clawdbot` 与 `claw-jijin-dogami` 的职责边界
- 明确核心领域对象与 API 抽象

交付物：

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT-FLOW.md`

### Phase 1：领域模型与存储

目标：

- 定义用户、组合、交易、基金快照、事件、建议、异步任务等模型
- 决定数据库与表结构
- 约束点位快照和回放边界

建议优先完成：

- `UserIdentity`
- `ChannelBinding`
- `Portfolio`
- `HoldingLot`
- `FundSnapshot`
- `MarketEvent`
- `AsyncJob`

### Phase 2：数据层

目标：

- 接入 `xalpha`
- 接入 `AKShare`
- 接入 `efinance`
- 建立本地缓存与快照存储

建议先做：

- 组合导入
- 基金净值同步
- 基金基础信息同步
- 基金公开持仓同步

### Phase 3：服务接口层

目标：

- 提供稳定的同步与异步 API
- 保证同一能力可以被页面与聊天共用

建议优先实现：

- `POST /v1/portfolio/analyze`
- `POST /v1/event/impact`
- `POST /v1/jobs/replay`
- `GET /v1/jobs/{job_id}`

### Phase 4：规则层与建议层

目标：

- 计算组合风险与暴露
- 计算消息影响分
- 输出结构化建议

建议先做：

- 持仓集中度分析
- 风格重合分析
- 单条消息影响分析
- 基础建议规则

### Phase 5：入口集成

目标：

- 先接页面
- 后接 OneBot

推荐原因：

- 页面更适合验证复杂结果和图表
- 聊天入口更适合在接口稳定后补充

### Phase 6：历史回放与评测

目标：

- 完成 point-in-time 快照
- 建立 walk-forward 评测闭环
- 用真实历史检验 AI 分析与策略

## 3. 每个阶段的交付标准

每进入下一阶段前，至少满足：

- 文档可读
- 接口命名稳定
- 数据结构清晰
- 能做最小闭环验证

## 4. 推荐的提交节奏

建议每一轮开发按以下顺序推进：

1. 写或更新设计文档
2. 补最小实现
3. 补最小验证
4. 提交 git

推荐提交风格：

- `docs: define service architecture`
- `feat: add portfolio domain models`
- `feat: add replay job api`
- `test: cover event impact scoring`

## 5. 当前阶段后的下一步

当前文档阶段完成后，下一步建议直接进入：

### 下一步优先级 1

先定义项目目录与领域模型骨架。

### 下一步优先级 2

定义服务 API 输入输出结构。

### 下一步优先级 3

再接入第一批真实基金数据能力。

