# 量化交易學習路線

一套 24 週、每週約 8–10 小時的量化交易自學與實務訓練計畫。

## 目標

完成以下完整流程：

```text
提出假設 → 取得資料 → 建立特徵 → 產生訊號 → 回測 → 驗證 → 風險管理 → 紙上交易
```

本計畫以股票／ETF 日線策略為起點，先建立可靠的研究流程，再進入機器學習與模擬交易。它不是獲利保證，也不是投資建議。

## 目錄

- [24 週學習路線](curriculum/24-week-roadmap.md)
- [每週自查表](curriculum/weekly-checklist.md)
- [每日自查表](curriculum/daily-checklist.md)
- [回測安全檢查表](curriculum/backtest-checklist.md)
- [紙上交易檢查表](curriculum/paper-trading-checklist.md)
- [每週回顧模板](templates/weekly-review.md)

## 教材代號

| 代號 | 教材 | 用途 |
|---|---|---|
| A | Ernest P. Chan, *Quantitative Trading* | 量化交易流程、策略、回測與實務框架 |
| B | Georgia Tech CS 7646: Machine Learning for Trading | 金融資料、計算投資與機器學習交易 |
| C | *An Introduction to Statistical Learning with Python* | 統計學習、迴歸、分類、重抽樣、正則化與樹模型 |
| D | Stefan Jansen, *Machine Learning for Trading* | 資料、特徵、模型、回測、投資組合、風險與部署 |
| E | pandas User Guide | DataFrame、時間序列、缺失值、rolling、shift、resample |
| F | scikit-learn User Guide | 模型訓練、評估、交叉驗證與特徵選擇 |
| G | statsmodels User Guide | 迴歸、統計模型與時間序列 |
| H | Marcos López de Prado, *Advances in Financial Machine Learning* | 金融資料洩漏、標籤、交叉驗證與回測過度擬合 |
| I | 研究日誌與策略報告 | 將教材轉化為自己的研究流程 |

## 每週固定節奏

- 星期一：閱讀教材 60–90 分鐘
- 星期二：重現教材範例 60–90 分鐘
- 星期三：改寫成自己的資料 60–90 分鐘
- 星期四：做實驗 60–90 分鐘
- 星期五：分析結果與找錯誤 60–90 分鐘
- 星期六：完成週專案 2–3 小時
- 星期日：回顧與自查 30–60 分鐘

## 狀態標記

```text
⬜ 尚未開始   🔵 進行中   ✅ 已完成   ⚠️ 需要重做   ⏸ 暫停
```

## 重要原則

1. 每週至少完成一個教材主題、一個程式實作、一個實驗和一份紀錄。
2. 所有策略先做日線、無槓桿、長期紙上交易。
3. 回測必須納入交易成本、滑價、訊號延遲與樣本外測試。
4. 在完成資料、回測、風險與模擬交易檢查前，不把回測視為可實盤策略。
