# Auto Shift Input Method

在 Windows 的繁體中文輸入法啟用時：

- 左 Shift：固定切換成英文輸入
- 右 Shift：固定切換成中文輸入

使用工作區的 Python 環境啟動：

```powershell
.\env\Scripts\pip.exe install -r .\requirements.txt
.\env\Scripts\python.exe .\auto_shift_input.py
```

程式會在右下角系統匣建立圖示；右鍵點擊圖示並選擇「結束程式」即可關閉。若不想顯示 CMD 視窗，請使用 `pythonw.exe` 啟動：

```powershell
.\env\Scripts\pythonw.exe .\auto_shift_input.py
```

它只會攔截繁體中文鍵盤配置（`zh-TW`、`zh-HK`、`zh-MO`），其他鍵盤配置的 Shift 行為不變。