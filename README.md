# CS Paper to Presentation PPT

把计算机论文做成能讲懂正文的中文汇报：先翻译和核对，再拆解讲解点，按论文顺序组织页面，配论文原图、口语化逐字稿和备用问答。

An open-source agent skill for Chinese computer-science paper presentations. It prioritizes faithful reading, source-linked figures, clear spoken explanations, and editable slides in the user's own template.

## 适合什么任务

- 从论文 PDF 制作组会或课程汇报 PPT。
- 把已有中文翻译转换为讲解点、大纲和口语讲稿。
- 按指定模板制作完整汇报，或只小修几页、只改备注。
- 在主讲后准备简短问答，并区分论文证据、解释和个人判断。

默认按 **30分钟主讲 + 10—15分钟问答、约五章** 组织，用户要求优先。章节顺序大致沿用论文，不固定页数，也不强迫每页只有三个点。

## 它是什么，不是什么

这是一个给支持本地 Skills 的智能体使用的工作流技能，不是独立的 PDF 转 PPT 程序。Python 脚本只负责安装、提取与检查；安装后不会自动调用模型，也不会自动开始转换。

实际生成 PPTX 需要宿主具备幻灯片制作与渲染能力。没有相应能力时，技能应明确停在翻译、大纲或讲稿阶段，不能把未执行的生成与检查说成已完成。模型、API 或宿主软件可能另行收费，本仓库不提供、不读取也不要求提交 API 密钥。

## 安装

需要 Python 3.10 或更高版本，安装脚本仅使用标准库。

```bash
git clone https://github.com/navybunny/CS-Paper-to-Presentation-PPT.git
cd CS-Paper-to-Presentation-PPT
python scripts/install.py
```

默认安装到 `CODEX_HOME/skills/cs-paper-to-presentation-ppt`；未设置 `CODEX_HOME` 时使用用户目录下的 `.codex/skills`。不覆盖已有同名技能，不修改其他技能或全局配置。安装后在新的对话回合中使用；若宿主尚未发现技能，按宿主说明重新加载技能列表。

自定义安装目录：

```bash
python scripts/install.py --dest /path/to/skills
```

也可让支持 GitHub 安装的技能安装器安装仓库中的 `skills/cs-paper-to-presentation-ppt`。其他宿主可按其说明加载该文件夹，具体兼容性未逐一验证。

## 怎样使用

准备论文 PDF，以及你有权使用的 PPTX 模板或历史样稿。已有译文、汇报时间、老师意见也可以一起提供。

```text
使用 $cs-paper-to-presentation-ppt。

原文：我的论文.pdf
模板：我的模板.pptx
参考风格：我之前的汇报.pptx
主讲30分钟，问答10分钟。

先核对中文翻译，按论文章节拆解讲解点，再完成五章PPT。
实验表格用原文截图，逐字稿直接写进备注。
这次直接完成，不用停在大纲确认。另存新文件，不覆盖参考稿。
```

局部修改：

```text
使用 $cs-paper-to-presentation-ppt。
只调整第10—12页的备注，以我提供的译文为主做口语化说明。
少量结合图中案例，不逐个描述箭头。其他页面和排版不要改。
```

英文用户也可直接说明任务：

```text
Use $cs-paper-to-presentation-ppt to create a Chinese paper talk from the
attached PDF and my PPTX template. Follow the paper's order, use original
figure/table crops, and put spoken scripts and backup Q&A in speaker notes.
```

没有模板时先确认视觉要求，再使用宿主提供的普通主题，不假装仓库附带某个学校的模板。

## 核心流程

1. 通读原文，弄清研究问题、方法、输入输出和实验关系。
2. 完整翻译正文或核对已有译文，保留章节、公式、条件与限制。
3. 根据译文的自然结构拆讲解点，建立章节、图表与页面对应关系。
4. 按论文顺序组织约五章，给出逐页大纲。用户要求直接完成时继续制作。
5. 相关工作讲清前人怎样做、困难在哪、本文从哪里切入，页底给出处。
6. 用原文图表与必要代码、目录、产物说明方法，不用装饰图代替证据。
7. 按用户模板制作可编辑页面，同步写自然口语讲稿。
8. 检查数字、分母、比较对象和证据范围，实际渲染后修复排版。

每页备注区分三个部分：

```text
【逐字稿】
可以直接口播的解释，不是对图片位置的流水描述。

【问答备用，不口播】
问：本页最可能被追问什么？
答：用几句话准确回答。

【原文定位与来源】
章节、PDF页码、图表编号、必要附录或外部来源。
```

## 辅助脚本

只读提取 PPTX 的真实放映顺序、页面文字、备注、字体及基础引用检查：

```bash
python skills/cs-paper-to-presentation-ppt/scripts/inspect_deck.py talk.pptx --output /path/to/work/inspection.json
```

在安装了桌面版 PowerPoint 的 Windows 上只读导出预览：

```powershell
./skills/cs-paper-to-presentation-ppt/scripts/render_deck.ps1 -InputPath 'C:\work\talk.pptx' -OutputDirectory 'C:\work\preview'
```

输出目录应在本次工作区且为空。其他系统可使用宿主自己的渲染功能。提取与渲染都不能代替事实核查，脚本也不生成 PPT。

## 验证范围和限制

发布前，个人原型曾在 Windows + PowerPoint 环境中对 RPG 与 Specine 两篇论文完成端到端试做，分别生成35页和33页汇报，包含讲稿与备用页。为保护个人信息及第三方内容，这些私人样稿、论文 PDF 和学校模板没有随仓库发布。

开源包另用合成 PPTX 测试页序、备注提取、隐藏页标记和安装行为。CI不调用大模型，也不证明新论文汇报的事实准确性或排版质量。Linux/macOS 上的完整幻灯片生成效果尚未验证。详见 [测试范围](docs/testing.md)。

## 隐私和素材边界

- 不含个人目录、账号密钥、校徽、校园背景、历史汇报、论文全文或商业插件源码。
- 本地私人模板版保持独立，开源版不依赖其中的文件或路径。
- 不要将未发表论文、实验数据、可识别学生的信息或带个人备注的完整 PPT 上传到公开 Issue。
- 本仓库的 MIT 许可证只覆盖本仓库提供的代码和说明，不授予第三方论文、图表、字体、模板的再分发权。

## 反馈与贡献

欢迎通过 [Issues](https://github.com/navybunny/CS-Paper-to-Presentation-PPT/issues) 报告问题或提出建议，也欢迎提交 Pull Request。

反馈尽量包括：使用的宿主与版本、论文类型、预期效果、实际问题，以及已脱敏的最小例子。区分事实错误、漏讲、图表截图、版式和讲稿问题，会更容易复现。不要提交 API 密钥或私人材料。

修改脚本后运行：

```bash
python -m unittest discover -s tests -v
```

更详细的贡献说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)，维护者：[navybunny](https://github.com/navybunny)。
