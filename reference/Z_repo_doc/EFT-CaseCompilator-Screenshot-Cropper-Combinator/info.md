# EFT-CaseCompilator-Screenshot-Cropper-Combinator

逃離塔科夫截圖處理工具。

## 功能

- **裁剪（case_crop.py）**：自動辨識遊戲中容器截圖的左上角和右下角，裁切出容器區域
- **拼接（case_concatenator.py）**：將多張裁剪後的圖片垂直拼接成一張長圖

## 運行原理

### case_crop.py — 模板匹配裁剪

1. 準備兩張角落範本圖：`corner_upper_left.png`（容器左上角邊框）和 `corner_lower_right.png`（右下角邊框）
2. 對 `input/` 中每張截圖，使用 OpenCV 的 `cv2.matchTemplate` 搭配 `TM_SQDIFF_NORMED`（歸一化平方差匹配）分別搜尋兩個角落的位置
3. 取 `cv2.minMaxLoc` 找到最佳匹配座標
4. 以左上角為起點、右下角為終點，裁切出容器區域，存入 `output/`

### case_concatenator.py — 垂直拼接

1. 讀取 `output/` 中所有 PNG（跳過先前輸出的 `big long boi*.png`）
2. 以最寬圖片為基準，用 `cv2.resize` + `INTER_CUBIC` 等比縮放其他圖片至相同寬度
3. 用 `cv2.vconcat` 垂直串接所有圖片
4. 輸出 `big long boi.png`，並依序縮小為 50%、25%、10% 三種版本

## 依賴關係

- Python 3.x
- `opencv-python`（cv2）
- `numpy`

（來源：`case_crop.py` 第 6-7 行、`case_concatenator.py` 第 1-2 行）
