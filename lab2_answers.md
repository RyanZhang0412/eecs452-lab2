# EECS 452 Lab 2 — 完整解读与答案

> 脚本目录：`LAB2_script/`  
> Prelab 图片与图表：`report_assets/`  
> 在 Raspberry Pi 上运行：`cd LAB2_script && python lab2_picamera2.py`

---

# Part 0 — Pre-Lab (Q1–Q7)

## 目标

用 MATLAB 理解 RGB/HSV，为 in-lab 的 **H 通道颜色阈值** 做铺垫。

## 答案摘要

| 题 | 要点 |
|----|------|
| Q1 | RGB = 红绿蓝强度；HSV = 色相/饱和度/明度，更适合颜色分割 |
| Q2 | 只差 V → 同颜色、不同亮暗 |
| Q3 | 只差 R → 偏红程度不同 |
| Q4 | Mid 图：RGB 三通道宽峰相关；HSV 的 H 多峰、S 左偏、V 双峰 |
| Q5 | min→max：R/G/B 同步升高 |
| Q6 | min→max：V 升最多，H 较稳，S 下降 |
| Q7 | 与文献一致，支持用 H 做阈值 |

详细数据见 `report_assets/prelab_q4_histograms.png`、`prelab_q5q6_means.png`。  
MATLAB 脚本：`LAB2_script/prelab_analyze.m`

### 英文短答（Prelab）

**Q1.** RGB = red/green/blue intensities for display/capture. HSV = hue/saturation/value; better for color segmentation under lighting changes.

**Q2.** Same hue/saturation, different brightness.

**Q3.** Different redness; higher R looks warmer/more red.

**Q4.** RGB histograms are broad and correlated; HSV H is multimodal, S left-skewed, V bimodal.

**Q5.** R, G, B all increase from min to max light.

**Q6.** V increases strongly; H changes moderately; S decreases.

**Q7.** Yes—RGB couples brightness into all channels; HSV isolates brightness in V, so H is more stable.

---

# Part 1 — Video Capture (Q8–Q12)

## 本节在做什么

在 Pi 上用 **Picamera2 + 环形缓冲** 实时取帧，理解 OpenCV 显示与 RGB/BGR 差异，并采样橙色球的 RGB。

## 代码位置

`LAB2_script/lab2_picamera2.py` — 主循环、`'c'` 键截图、RGB→BGR 显示修复。

---

### Q8. Circular buffer vs `capture_image()` every loop?

**环形缓冲的好处：**

1. **更低延迟**：相机持续写入缓冲，主循环只读最新帧，不必每帧阻塞等待一次完整 capture。
2. **更稳定帧率**：避免 capture 与处理串行造成的抖动。
3. **减少丢帧/卡顿**：处理慢时仍能拿到较新的帧，而不是排队等旧 capture 完成。
4. **与编码器配合**：H264 编码器 + CircularOutput 可在后台持续接收数据。

---

### Q9. What does `1` in `cv2.waitKey(1)` mean? Can OpenCV wait less?

`waitKey(1)` 表示最多等待 **1 毫秒** 看是否有按键。

- `waitKey(0)`：无限等待
- `waitKey(n)`：等待 n 毫秒

**不能等待少于 1 ms**（参数是整数毫秒，最小有效值为 1）。

---

### Q10. Why are colors wrong in the displayed image?

OpenCV 默认按 **BGR** 解释彩色图像，而 Picamera2 输出的是 **RGB888**。  
不转换时，红蓝通道对调，颜色发紫/发青。

**修复**：`cv2.cvtColor(image, cv2.COLOR_RGB2BGR)` 再 `imshow`。

---

### Q11. Typical RGB pixel value for the orange ball?

在 Pi 上用 `'c'` + pyplot 鼠标读取球表面像素：

**典型 RGB ≈ (238, 183, 5)**

（高 R/G、极低 B；截图见 `report_assets/BallRGB_Q11.png`。）

对应 OpenCV HSV 的 H 约 **10–25**（0–179 刻度）；调参后使用 **H = 13**。

---

### Q12. Report screenshot

在 Pi 上运行后截屏，需同时显示：

- OpenCV 窗口（Raw / Difference / Binary）
- pyplot 的 `'c'` 捕获图

---

# Part 2 — Color Thresholding (Q13–Q19)

## 本节在做什么

1. 转 HSV，取 **H 通道** 与目标 H 做差 → 差分图  
2. **boxFilter** 降噪  
3. **threshold** → 二值图（球为白）  
4. **Trackbar** 在线调 H 和阈值

## 算法流程

```
RGB frame → HSV → |H - H_val| → boxFilter(5×5) → threshold → binary mask
```

---

### Q13. Chosen H-value?

默认起始 **H_val = 15**（OpenCV 0–179）。  
用 trackbar 微调，使差分图中球最暗、背景最亮。

---

### Q14. What color is the ball in the difference image?

**暗（低灰度）**。  
球像素 H 接近 H_val，差值小；背景 H 不同，差值大 → 球是暗斑，背景亮。

---

### Q15. Appropriate `threshold` type?

**`cv2.THRESH_BINARY_INV`**

- 差值 **低于** 阈值 → 255（白）→ 球  
- 差值 **高于** 阈值 → 0（黑）→ 背景  

---

### Q16. Shape after `boxFilter`?

**与输入相同**：`(height, width)`，例如 `(480, 640)`。  
`boxFilter` 只平滑像素值，不改变尺寸（`ddepth=-1` 保持深度）。

---

### Q17. Five arguments to `createTrackbar`?

| 参数 | 含义 |
|------|------|
| `trackbarName` | 滑条名称（如 `"H-value"`） |
| `windowName` | 所属窗口名 |
| `value` | 初始值 |
| `count` | 最大值（滑条上界） |
| `onChange` | 回调函数（可为 `nothing`） |

---

### Q18. Tuned H-value and threshold?

实测调参结果：

- **H-value**：**13**  
- **Threshold**：**13**  

以二值图中只有球为白、背景噪声最少为准（见 Q19 截图）。

---

### Q19. Example binary image

见 `report_assets/Binary_Q19.png`（Binary Image 窗口，H=13, Threshold=13）。

---

# Part 3 — Timing (Q20–Q22)

## 本节在做什么

实现 `timer.py`，测量各阶段耗时，分析实时性能瓶颈。

## 代码

- `LAB2_script/timer.py` — `time.time()` 计时  
- `lab2_picamera2.py` — 三层 timer：总 color threshold / diff / box / thresh

---

### Q20. Execution times (Pi 实测, 640×480, index-image 模式)

代表帧：`Frame processed in 0.0922 s (10.84 frames per second)`

| 阶段 | 实测 |
|------|------|
| Color thresholding（整体） | **0.023132 s** |
| Display images | **0.001799 s** |
| One full frame | **0.0922 s** |

---

### Q21. Frames per second?

该帧：**10.84 FPS**（同模式下大致 9–12 FPS）。

---

### Q22. Color thresholding breakdown

同一代表帧：

| 子步骤 | 实测 |
|--------|------|
| Difference image | **0.013107 s** |
| Box filter | **0.001741 s** |
| Threshold | **0.007897 s** |

本机上 difference / threshold（含形态学清理）比 box filter 更耗时；整体 color threshold 仍远快于双重循环定位。

---

# Part 4 — Ball Localization (Q23–Q25)

## 本节在做什么

从二值图求质心 `(Cx, Cy)` 和半径：

\[
C_x = \frac{\sum x_i}{k}, \quad C_y = \frac{\sum y_i}{k}, \quad r = \sqrt{\frac{k}{\pi}}
\]

两种实现：

1. **双重 for 循环**（慢，纯 Python）  
2. **Index image + NumPy**（快，矩阵运算）

## 代码

`identify_ball()` 中两种分支；切换 `USE_IDX_IMG = True/False`。

Index image 思路：

- `x_idx`：每列是该列 x 坐标  
- `y_idx`：每行是该行 y 坐标  
- 用二值 mask 加权求和 → 质心

---

### Q23. Heuristic (nested loop) timing?

`USE_IDX_IMG = False`，代表帧：

`Frame processed in 2.5258 s (0.40 frames per second)` → `contours: 2.377461 s`

| 指标 | 实测 |
|------|------|
| Localization | **2.377461 s** |
| FPS | **0.40 FPS** |

Python 双重循环遍历 640×480 ≈ 30 万像素，几乎占满整帧时间。

---

### Q24. Index image method timing?

`USE_IDX_IMG = True`，代表帧：

`Frame processed in 0.0922 s (10.84 frames per second)` → `contours: 0.010873 s`

| 指标 | 实测 |
|------|------|
| Localization | **0.010873 s** |
| FPS | **10.84 FPS** |

相对双重循环，定位约快 **200×**（2.38 s → 0.011 s），帧率从 ~0.4 提到 ~11 FPS。

---

### Q25. Demonstrate index image works

在 Pi 上：

1. 设 `USE_IDX_IMG = True`  
2. 录制短视频或截屏：原图 + 绿色检测圆  
3. 球移动时圆心应跟随

---

# Part 5 — Post-Lab (Q26–Q29)

---

### Q26. Compare the two localization methods

**双重循环**：实现直观、易调试，但在 Pi 上极慢，帧率不足以实时跟踪；对噪声敏感但逻辑简单。

**Index image**：利用 NumPy 矩阵运算，速度提升显著，精度与循环法相同（同一公式）；内存略增（index 向量），但可预先计算。

**结论**：实时系统应使用 index image（或进一步优化/OpenCV contours）；循环法仅适合理解算法、离线验证。

---

### Q27. Python vs C++

**A) Interpreted vs compiled**

- **编译型**（C++）：源码→机器码，运行快；需编译步骤。  
- **解释型**（Python）：逐行解释/字节码，开发快、运行较慢。  
- Python = 解释型；C++ = 编译型。

**B) Dynamic vs static typing**

- **静态类型**（C++）：编译期检查类型，类型错误早暴露，通常更快。  
- **动态类型**（Python）：运行时确定类型，灵活但开销更大。  
- Python = 动态；C++ = 静态。

**C) Garbage collection**

- **GC 优点**：自动内存管理，减少泄漏/悬空指针。  
- **GC 缺点**：不可预测停顿、额外开销。  
- Python 有 GC；C++ 无内置 GC，手动/`smart_ptr` 管理。

---

### Q28. C++ OpenCV on Raspberry Pi

**A) Import OpenCV in C++**

```cpp
#include <opencv2/opencv.hpp>
// 或具体模块
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
```

**B) Compile on Raspbian**

典型流程（CMake + g++）：

```bash
mkdir build && cd build
cmake ..
make
./your_program
```

or：`g++ main.cpp -o app `pkg-config --cflags --libs opencv4``

参考：[OpenCV Linux GCC CMake Tutorial](https://docs.opencv.org/4.6.0/db/df5/tutorial_linux_gcc_cmake.html)

---

### Q29. OpenCV Python vs C++ performance

**A) Why is Python slower?**

1. Python 调用 OpenCV 时多数函数仍走 **C++ 后端**，但 Python 层有序列化/类型转换/GIL 开销。  
2. **纯 Python 循环**（如未向量化的 centroid）极慢。  
3. 解释器本身开销；NumPy 向量化的部分差距会缩小。

**B) Why use Python anyway?**

- 开发速度快、代码简洁  
- 原型验证后再用 C++ 优化热点  
- OpenCV Python 绑定对多数图像操作已足够快  
- 与 matplotlib、picamera 等生态集成方便  

---

# 附录 — 文件结构

```
lab2/
├── lab2_answers.md          ← 本文件
├── prelab_answers.md        ← Prelab 精简版（可删）
├── lab2.pdf
├── LAB2_script/
│   ├── lab2_picamera2.py    ← 主程序（Pi）
│   ├── timer.py
│   └── prelab_analyze.m     ← Prelab 分析（PC/MATLAB）
└── report_assets/
    ├── fruit_*_light.jpg
    └── prelab_*.png
```

## Pi 运行 checklist

- [ ] `pip install opencv-python picamera2 numpy matplotlib`
- [ ] 相机权限已开
- [ ] `cd LAB2_script && python lab2_picamera2.py`
- [ ] 用 trackbar 调 H / Threshold
- [ ] `'c'` 截图，`'q'` 退出
- [ ] 切换 `USE_IDX_IMG` 对比 Q23/Q24 计时

---

# Canvas 英文汇总（In-Lab + Post-Lab）

**Q8.** A circular buffer lets the camera continuously capture in the background so the main loop reads the latest frame with lower latency and more stable frame rate, instead of blocking on a fresh capture every iteration.

**Q9.** The `1` means wait up to 1 ms for a keypress. OpenCV cannot wait less than 1 ms because the argument is in whole milliseconds.

**Q10.** Colors look wrong because OpenCV expects BGR order while Picamera2 outputs RGB. Fix with `cv2.cvtColor(image, cv2.COLOR_RGB2BGR)`.

**Q11.** Example orange-ball RGB (measure on your ball): about (205, 115, 45).

**Q13.** Starting H-value: 15 (OpenCV 0–179 scale), tuned with trackbar.

**Q14.** The ball appears dark (low difference) in the difference image.

**Q15.** Use `cv2.THRESH_BINARY_INV` so low-difference ball pixels become white.

**Q16.** Same shape as the input difference image, e.g. (480, 640).

**Q17.** Arguments: trackbar name, window name, initial value, maximum value, callback function.

**Q18.** Tuned values: H-value = 13, Threshold = 13.

**Q20.** Color thresholding 0.023132 s; display 0.001799 s; one frame 0.0922 s.

**Q21.** 10.84 FPS (representative frame).

**Q22.** Diff 0.013107 s; box filter 0.001741 s; threshold 0.007897 s.

**Q23.** Nested-loop localization 2.377461 s; 0.40 FPS.

**Q24.** Index-image localization 0.010873 s; 10.84 FPS.

**Q26.** Nested loops are easy to understand but too slow for real-time tracking; the index-image NumPy method gives the same centroid/radius much faster.

**Q27A.** Compiled languages translate to machine code (C++); interpreted languages execute via an interpreter (Python).

**Q27B.** Static typing checks types at compile time (C++); dynamic typing resolves types at runtime (Python).

**Q27C.** GC simplifies memory management but adds overhead; Python has GC, C++ does not by default.

**Q28A.** `#include <opencv2/opencv.hpp>`

**Q28B.** Build with CMake/make or g++ with `pkg-config --cflags --libs opencv4`.

**Q29A.** Python overhead from interpreter, GIL, and non-vectorized code; many OpenCV calls still run C++ underneath.

**Q29B.** Faster development, easier prototyping, good enough performance when using NumPy/OpenCV vector operations.
