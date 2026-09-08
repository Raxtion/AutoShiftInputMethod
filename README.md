# Auto Shift Input Method


受夠在Windows打中文字一直按錯輸入法導致不斷重複按刪除鍵嗎? 
啟動 Start_auto_shift_input.bat 讓Windows明確知道 你現在正在使用哪一種輸入法 (左shift強制轉中文, 右側shift強制轉英文, 或反之則反)

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

已知問題: Windows Notepad 記事本軟體 的輸入法變更方式與其他桌面軟體不一樣, 在記事本使用這個軟體功能, 會有所限制, 需要使用者注意一下.
微軟應該將這個功能 直接內建在Windows 才對.
這是為 "公司工作電腦" 所Vibe Coding的功能. 因為工作電腦不允許安裝第3方按鍵快速鍵軟體(資安問題).
