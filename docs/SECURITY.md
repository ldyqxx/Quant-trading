# 安全注意事項 / Security Guidelines

> ⚠️ 量化交易系統涉及真實資金，請嚴格遵守以下安全規範。
> ⚠️ Quant trading systems involve real money. Please strictly follow these security guidelines.

---

## 目錄 / Table of Contents

1. [API Key 管理](#api-key-管理)
2. [Docker 安全配置](#docker-安全配置)
3. [網絡安全](#網絡安全)
4. [交易所安全設定](#交易所安全設定)
5. [日誌安全](#日誌安全)
6. [備份安全](#備份安全)
7. [事件響應](#事件響應)

---

## API Key 管理 / API Key Management

### 絕對禁止 / Never Do This

- ❌ **不要**將真實 API Keys 提交到 Git 倉庫
- ❌ **不要**在聊天軟件、郵件或截圖中分享 API Keys
- ❌ **不要**使用允許提款的交易所 API Keys（僅需交易權限）
- ❌ **不要**與他人共用 API Keys

### 正確做法 / Best Practices

- ✅ 將密鑰存儲在 `.env` 文件中（已在 `.gitignore` 中排除）
- ✅ 交易所 API Keys 僅開啟「現貨交易」和「讀取」權限，**關閉提款權限**
- ✅ 設定交易所 API 的 IP 白名單，僅允許您的伺服器 IP
- ✅ 定期輪換 API Keys（建議每 90 天）
- ✅ 為不同環境（測試/生產）使用不同的 API Keys

### 驗證 .env 未被提交

```bash
# 確認 .env 在 .gitignore 中
cat .gitignore | grep "^\.env$"

# 確認 .env 沒有在 Git 追蹤中
git ls-files .env
# 應該無輸出
```

---

## Docker 安全配置 / Docker Security Configuration

### 端口暴露 / Port Exposure

`docker-compose.yml` 中已將 OpenClaw 綁定到 `127.0.0.1:18789`，**不對外暴露**：

```yaml
ports:
  - "127.0.0.1:18789:18789"  # ✅ 僅本機訪問
  # 避免：
  # - "18789:18789"           # ❌ 對所有 IP 開放
  # - "0.0.0.0:18789:18789"  # ❌ 對所有 IP 開放
```

### 掛載目錄只讀 / Read-Only Mounts

配置和策略目錄以只讀模式掛載：

```yaml
volumes:
  - ./config:/app/config:ro       # ✅ 只讀
  - ./strategies:/app/strategies:ro # ✅ 只讀
  - ./logs:/app/logs              # 可寫（記錄日誌）
```

### 避免使用 root 用戶 / Avoid Running as Root

建議在生產環境中，使用非 root 用戶運行 Docker：

```bash
# 創建專用用戶
sudo adduser --system --no-create-home quantbot
sudo usermod -aG docker quantbot
```

---

## 網絡安全 / Network Security

### SSH 安全強化 / SSH Hardening

```bash
# /etc/ssh/sshd_config
PermitRootLogin no           # 禁止 root 登入
PasswordAuthentication no    # 禁用密碼認證
PubkeyAuthentication yes     # 啟用 Key 認證
MaxAuthTries 3               # 最多嘗試 3 次
```

### 防火牆設定 / Firewall Configuration

```bash
# 使用 UFW（Ubuntu）
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH（或使用非標準端口）
ufw enable

# 禁止直接訪問 OpenClaw 端口（已通過 127.0.0.1 綁定保護）
# 如需外部訪問，使用 SSH 隧道：
# ssh -L 18789:localhost:18789 user@your-server
```

### 使用 SSH 隧道遠程訪問 / SSH Tunnel for Remote Access

```bash
# 在本地機器上執行
ssh -L 18789:localhost:18789 user@your-vps-ip

# 然後在本地瀏覽器訪問
# http://localhost:18789
```

---

## 交易所安全設定 / Exchange Security Settings

### Binance API 設定建議

1. 進入 API Management → 創建新 API
2. 僅勾選：
   - ✅ **Enable Reading** — 讀取賬戶信息
   - ✅ **Enable Spot & Margin Trading** — 現貨交易
   - ❌ **Enable Withdrawals** — **不要勾選**
   - ❌ **Enable Futures** — 除非您的策略需要
3. 設定 **IP Access Restriction**，填入您 VPS 的 IP 地址

### OKX API 設定建議

1. 進入 API → 創建 API
2. 權限選擇：**交易（Trade）**，不勾選提款
3. 設定 IP 綁定

### 通用建議

- 為 API 設定每日提款限額（即使關閉提款權限也要設定）
- 啟用雙重驗證（2FA）
- 定期審查 API 使用日誌

---

## 日誌安全 / Log Security

### 敏感信息過濾 / Sensitive Data Filtering

確保日誌中不包含 API Keys 或敏感信息。如果需要調試，使用：

```bash
# 查看日誌時過濾敏感關鍵詞
docker compose logs openclaw | grep -v "api_key\|secret\|password"
```

### 日誌保留策略 / Log Retention

`docker-compose.yml` 已設定日誌大小限制：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # 每個日誌文件最大 10 MB
    max-file: "5"     # 保留最多 5 個文件
```

---

## 備份安全 / Backup Security

- ✅ 備份文件存儲在 `backups/`（已在 `.gitignore` 中排除）
- ✅ 備份文件不應包含 `.env`（腳本已排除）
- ✅ 如需離線備份，對備份文件加密：

```bash
# 加密備份文件
gpg --symmetric --cipher-algo AES256 backups/backup_20250101_120000.tar.gz

# 解密
gpg --decrypt backups/backup_20250101_120000.tar.gz.gpg > backup.tar.gz
```

---

## 事件響應 / Incident Response

### 發現 API Key 洩露時 / If API Key is Compromised

1. **立即撤銷**洩露的 API Key（在交易所後台操作）
2. **停止** OpenClaw 服務：`docker compose down`
3. 生成**新的 API Key** 並更新 `.env`
4. 檢查交易記錄，確認是否有異常交易
5. 重新啟動服務：`docker compose up -d`

### 發現異常交易時 / If Suspicious Trades Detected

1. 立即停止服務：`docker compose down`
2. 切換到 paper 模式：修改 `.env` 中的 `TRADING_MODE=paper`
3. 審查 `logs/` 目錄中的交易日誌
4. 聯繫交易所客服

### 緊急停止命令 / Emergency Stop Commands

```bash
# 停止所有服務
docker compose down

# 強制停止容器
docker kill openclaw-quant

# 查看最後 100 行日誌
docker compose logs --tail 100 openclaw
```

---

## 安全自查清單 / Security Checklist

在上線前，請確認以下項目：

- [ ] `.env` 文件不在 Git 追蹤中（`git ls-files .env` 無輸出）
- [ ] 交易所 API 已關閉提款權限
- [ ] 交易所 API 已設定 IP 白名單
- [ ] 防火牆已阻止外部直接訪問 18789 端口
- [ ] 已使用 paper 模式測試至少一週
- [ ] 已設定合理的 `RISK_LIMIT_PCT` 和 `MAX_POSITION_SIZE`
- [ ] 已測試備份腳本
- [ ] 已設定監控告警（建議使用 Uptime Kuma 或類似工具）
