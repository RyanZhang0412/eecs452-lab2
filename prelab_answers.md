# EECS 452 Lab 2 — Pre-Lab 解读与答案

> 提交到 Canvas：**Pre Lab 2**。不必提交具体 RGB/HSV 数组，只描述趋势。
>
> 已用工作区图片分析：`fruit_min_light.jpg` / `fruit_mid_light.jpg` / `fruit_max_light.jpg`  
> 附图：`prelab_q4_histograms.png`、`prelab_q5q6_means.png`

---

## Prelab 在做什么（解读）

Lab 2 的核心是**用颜色阈值跟踪橙色球**。Prelab 先用 MATLAB 搞清楚：

1. **图像表示**：`imread` → 通常 `M×N×3` 的 `uint8`
2. **RGB vs HSV**：哪种更适合“光照变化下仍能认出同一种颜色”

In-lab 会用 **HSV 的 H 通道**做差分阈值；Prelab 就是为此铺垫。

---

## Q1. What are RGB and HSV values and what are they used for?

**RGB**（Red, Green, Blue）是加色模型：每个像素用红、绿、蓝强度合成颜色。显示器、相机、多数图像文件都以 RGB 存储。Matlab 彩色图通常是 `height × width × 3`（0–255）。

**HSV**（Hue, Saturation, Value）更接近感知：

| 通道 | 含义 |
|------|------|
| **H** | 色相：是什么颜色 |
| **S** | 饱和度：鲜艳程度 |
| **V** | 明度：亮暗 |

RGB 适合显示/硬件；HSV（尤其 H）常用于颜色分割与跟踪，因为光照主要影响 V，H 相对更稳。

---

## Q2. Two colors differ only in V. How do they differ visually?

同色相、同饱和度，但**明暗不同**：一个更亮、一个更暗。

---

## Q3. Two colors differ only in R. How do they differ visually?

红通道更大 → **更偏红/更暖**；红通道更小 → 红成分减弱，相对更偏青/冷。

---

## Q4. Mid-light：各通道直方图定性描述

对 `fruit_mid_light.jpg`（碗中水果俯视图）的实测直方图：

**RGB**

- **R**：大致单峰、较宽，质量集中在约 0.2–0.6（中等红强度；红苹果推高右侧）。
- **G**：略呈双峰，主峰约在 0.3–0.45（香蕉黄、绿苹果与纸盒贡献不同绿水平）。
- **B**：峰更尖，质量偏 0.35–0.55（桌布偏冷色，整体 B 不低）。
- 三通道形状相关但峰值位置不同，都反映“亮度 + 颜色”混在一起。

**HSV**

- **H**：多峰、离散。低端（~0–0.15）对应红/橙苹果；高端（~0.6–1.0）有强峰（桌布/背景偏蓝紫一类色相）。中间区间较空——这是色类聚类，不是亮度分布。
- **S**：严重左偏，主峰很低（~0.1），长尾到高饱和（鲜艳水果）；多数背景偏灰白。
- **V**：双峰约在 0.35–0.55，对应场景中等亮度区域。

**差异一句话**：RGB 三通道都是“强度”直方图、彼此相似；HSV 把色相拆成尖峰簇、饱和度左偏、明度单独成峰，形态明显不同。

---

## Q5. 光照 min → mid → max：RGB 如何变？

全图通道均值（归一化 0–1）：

|  | R | G | B |
|--|---|---|---|
| min | 0.18 | 0.18 | 0.22 |
| mid | 0.38 | 0.36 | 0.39 |
| max | 0.62 | 0.58 | 0.64 |

**R、G、B 几乎同步、近似线性上升**（直方图整体右移）。暗图细节挤在低端；强光图桌布/高光更亮，颜色被“冲淡”但仍体现在更高的 RGB 值上。固定 RGB 阈值很难跨光照使用。

---

## Q6. 光照 min → mid → max：HSV 如何变？

|  | H | S | V |
|--|---|---|---|
| min | 0.53 | 0.36 | 0.24 |
| mid | 0.57 | 0.25 | 0.43 |
| max | 0.66 | 0.20 | 0.68 |

- **V**：随光照**明显升高**（0.24 → 0.68），是主变化。
- **H**：相对最稳，但仍有一定漂移（暗噪/过曝会扰动色相均值）。
- **S**：随光增强而**下降**（强光冲淡、桌布更接近白 → 平均饱和度变低）。

---

## Q7. 是否与文献一致？

**基本一致，且本图还多验证了一点。**

文档指出 RGB 把亮度耦合进每个通道 → 我们看到 R/G/B 都随光强上升。HSV 把亮度主要放在 V → V 变化最大；H 比 RGB 更稳，更适合做颜色阈值（这也是 in-lab 用 H 的原因）。

本场景里 S 随光增强下降，也符合“高光照使颜色显得更淡/更接近白”的直觉；H 并非完全不变（极暗/过曝时仍会漂），但远小于 RGB 各通道的整体抬升幅度。

---

## Canvas 英文短答（可直接粘贴）

**Q1.** RGB represents color as red/green/blue intensities and is the native format for cameras/displays. HSV represents hue (color type), saturation (purity), and value (brightness). HSV is useful for color segmentation because it better separates chromaticity from lighting.

**Q2.** Same hue and saturation but different brightness—one appears lighter, the other darker.

**Q3.** They differ in redness: higher R looks more red/warmer; lower R looks less red (more cyan-shifted relative to G and B).

**Q4.** For the mid-light fruit image: R is a broad mid-range hump; G is somewhat bimodal; B is more peaked mid-high. In HSV, H is multimodal with separate clusters for red fruit vs cooler background; S is strongly left-skewed (mostly desaturated background, colorful fruit in the tail); V is bimodal in the mid-brightness range. RGB channels look like related intensity distributions, while HSV separates color class, purity, and brightness.

**Q5.** From min→mid→max, mean R/G/B all increase roughly together (about 0.18→0.38→0.62 for R; similar for G and B). Histograms shift right as the scene brightens.

**Q6.** V increases strongly with lighting (~0.24→0.43→0.68). H changes only moderately. S decreases as light increases (colors wash out / approach white).

**Q7.** Yes. RGB couples brightness into every channel, so all rise with illumination. HSV places most brightness change in V; H is more lighting-stable, matching the readings and motivating H-based thresholding. The drop in S under bright light also matches the idea that strong illumination can desaturate colors.
