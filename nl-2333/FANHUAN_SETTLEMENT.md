# 返利结算功能说明

## 功能说明

每日自动将前一日 USDT转TRX 的返利结算到指定代理地址，并发送「✅结算成功」通知给管理员。

**默认执行时间：每日 11:00**（可在配置文件中自定义）

## 默认行为（修复后）

**默认已关闭**。如需启用，在 `config.txt` 中添加：

```
enable_fanhuan_settlement=1
```

## 配置项

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `enable_fanhuan_settlement` | 是否启用每日返利结算 | `0`（关闭） |
| `fanhuan_settlement_address` | 代理收款地址 | `TKYp9dbDs6kHKtFhFR6srEJvDARNYkq9Qe` |
| `fanhuan_min_amount` | 最小结算金额（TRX），低于此值不执行 | `0.1` |
| `fanhuan_settlement_hour` | 结算执行时间（小时，0-23） | `11` |
| `fanhuan_settlement_minute` | 结算执行时间（分钟，0-59） | `0` |

## 示例

```txt
# 启用返利结算
enable_fanhuan_settlement=1
# 自定义代理地址（可选）
fanhuan_settlement_address=你的代理地址
# 最小结算 1 TRX（可选）
fanhuan_min_amount=1
# 自定义结算时间（可选，默认 11:00）
fanhuan_settlement_hour=11
fanhuan_settlement_minute=0
```

## 触发条件

1. `enable_fanhuan_settlement=1`
2. 当日有 USDT转TRX 交易（会写入 `transaction_records_YYYY-MM-DD.txt`）
3. 结算金额 ≥ `fanhuan_min_amount`（默认 0.1 TRX）
4. 已配置出款私钥（`usdt2trx_private_key` 或 `privateKey`）

## 修复说明（2026-02）

- **默认关闭**：避免未配置时误发通知
- **金额校验**：金额 ≤ 0 或 < 最小阈值时跳过，不再发送 0 TRX 转账
- **配置化**：代理地址、最小金额可配置
- **容错**：返利文件格式错误时跳过该行，不崩溃
