# 开发记录

一个"AI 用 AI 做的桌宠"，所以过程本身也算交付物的一部分。

## 时间线

| 阶段 | 做了什么 |
|---|---|
| 侦察 | 确认机器上有 Python 3.12 / tkinter 8.6、git 2.56、没有 gh CLI；验证 GitHub API 可用、令牌权限 `repo, workflow` |
| 技术选型 | 放弃 Electron（太重）、放弃网页（不能浮窗），选 tkinter + Win32 颜色键 |
| 精灵 | 手写 `tools/art.py`，四轮迭代：v1 空心脑袋 → v2 肩臂断开 → v3 比例失衡 → v4 定稿 |
| 程序 | 透明窗口 / 拖拽 / 动画时钟 / 状态机 / 气泡 / 右键菜单 / 配置持久化 |
| 第三形态 | 按参考图重画：九点白面具、金色护臂 + 紫色符文、肩上两只猫，并加命中框 |
| 测试 | 22 个单元测试；其中"颜色键不变量"和"CLIPS ↔ manifest 一致性"抓过真实 bug |
| 发布 | 建仓、开 issue、写 README / CI |

## 几个真正踩过的坑

1. **`tempfile.mkdtemp` 在受限环境里建出来的目录，自己反而写不进去**
   （ACL 只给创建者而沙箱令牌不匹配）。测试改用项目内自建目录，顺带避免了 Windows 临时目录被清理。
2. **颜色键必须严格等于 PNG 里的像素值**。一开始把精灵存成带 alpha 的 RGBA，
   结果 `-transparentcolor` 完全不生效，窗口是一整块洋红。改成 RGB + 纯色底才通。
3. **描边不能有抗锯齿**。Pillow 的 `ImageDraw` 本身是抗锯齿关闭的，所以边缘干净；
   一旦改用 `Image.resize(..., BILINEAR)` 放大，边缘立刻出现"半洋红"的脏边 —— 必须 NEAREST。
4. **气泡不能用透明色键**。文字抗锯齿会和洋红混出粉边，所以气泡单独开一个不透明小窗，
   用 `-alpha` 做整体淡入，反而更干净。
5. **切换形态会改窗口尺寸**，如果按左上角定位，脚会"跳"一下。改成以脚为锚点重算坐标。
6. **`-transparentcolor` 的透明像素天然可穿透**，所以不用额外算 `WS_EX_TRANSPARENT`，
   但这也意味着右键菜单要在"可见像素"上触发 —— 靠 `overrideredirect` + 精灵边界即可。

## 用到的工具

- 绘图：Pillow（仅构建期）
- 窗口：tkinter / Tk 8.6
- 测试：`unittest`
- CI：GitHub Actions（windows-latest × Python 3.10/3.12）
- 截图验证：`PIL.ImageGrab` + `--snapshot` 参数（真的把窗口截下来看过，不是"应该能跑"）

## 给后来者的建议

想复刻的话，最省时间的顺序是：

1. 先做 `--selftest` 和 `--snapshot`，**能截图再谈美术**；
2. 精灵先定"剪影"再抠细节，`assets/preview/sprite-sheet.png` 会随生成自动更新，方便对比；
3. 把"哪些像素可点"做成纯数据（`hotspots.py`），别让它依赖 Pillow；
4. 单测只保护**不变量**（颜色键、manifest 一致、命中框在画布内），别去测动画帧数这种会变的东西。
