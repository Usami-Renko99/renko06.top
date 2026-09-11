# Renko PDF-first Jekyll Site

这是一个适合数学笔记发布的 GitHub Pages / Jekyll 模板。核心原则是：

- `.pdf` 是网站发布对象；
- `.tex` 是可选源码；
- 只上传 PDF，网站就会自动生成 Notes 索引；
- 不需要为每篇笔记手写 Markdown 页面。

## 你以后需要做什么

把 PDF 放进对应分类目录，然后 push 即可。

推荐目录：

```text
assets/pdf/<category>/<filename>.pdf
```

例如：

```text
assets/pdf/algebraic-geometry/sheaves.pdf
assets/pdf/representation-theory/characters.pdf
```

网站会自动显示为：

```text
Sheaves
View PDF | Download

Characters
View PDF | Download
```

## 如果也想公开 TeX 源文件

TeX 不是必须的。只有当你想让别人查看源码时，才上传同名 `.tex`：

```text
assets/tex/algebraic-geometry/sheaves.tex
```

如果 PDF 和 TeX 的 category + filename 一致，网站会自动多显示一个 `TeX` 链接：

```text
Sheaves
View PDF | Download | TeX
```

## 发布 Blog 文章

Blog 文章放在 `_posts/`，文件名可以直接使用中文、英文或空格，不需要日期前缀。例如 `_posts/关于大模型的思考.md`：

```markdown
# 关于大模型的思考

这里直接写正文。
```

部署时会在临时副本中补齐文章配置，并转换成 Jekyll 需要的文件名；仓库中的原文件名和正文不会被自动改写。

自动规则：

- 标题：优先使用 front matter 的 `title`，其次取正文第一个一级标题，最后使用文件名（去掉已有日期前缀）。
- 日期：优先使用 `date`，其次取文件名的 `YYYY-MM-DD`，否则使用 Git 历史中该文件首次提交的作者时间，转换为北京时间。修改正文或重新部署不会刷新发布日期。
- 地址：默认根据日期和文件名生成，修改正文或正文标题不会改变地址。重命名文件或修改日期可能改变地址；需要固定地址时可手写 `permalink`。
- 封面：默认查找 `/assets/images/blog/<文件名去掉日期前缀>.jpg`，没有图片时不显示封面；可通过 `cover` 指定其他图片。
- 已有文章保留原有日期、地址和封面设置。生成文件名冲突时构建会报错，不会覆盖文章。
- 手写 front matter 是可选项；需要时必须从第一行开始。未来日期的文章默认不会发布。

可选配置示例：

```markdown
---
title: "文章标题"
date: 2026-06-17 20:00:00 +0800
---

这里开始写正文。
```

本地预览同样需要先准备临时副本（输出目录必须尚不存在）：

```bash
python3 -m pip install PyYAML==6.0.3
python3 scripts/ensure_post_front_matter.py --site-output-dir /tmp/blog-preview
bundle exec jekyll serve --source /tmp/blog-preview
```

尚未提交的新文件需要先提交到 Git，或手写 `date`。可以加 `--dry-run` 仅检查，不创建副本。旧的无参数调用仅补全配置并直接写回原文件，不负责自由文件名转换，发布和预览请使用上面的副本模式。

发布后，Blog 列表会在 `/blog/` 显示文章。

## Blog 封面图

封面图建议放在：

```text
assets/images/blog/
```

然后在文章 front matter 里加入：

```markdown
---
layout: post
title: "文章标题"
date: 2026-06-17 20:00:00 +0800
cover: /assets/images/blog/my-cover.jpg
cover_alt: "封面说明"
cover_caption: "可选的封面题注"
---
```

说明：

- `cover` 是封面图片路径；
- `cover_alt` 是图片替代文本，建议写；
- `cover_caption` 是封面下方题注，可写可不写；
- 没有 `cover` 的文章也会正常显示，只是不显示封面；
- 如果 `cover` 指向的本地图片不存在，网站也不会显示破图。

## Blog 附件 PDF

如果 PDF 只是 blog 的附件，不是正式数学笔记，不要放进 `assets/pdf/<category>/`，否则可能被 Notes 系统收录。建议放在：

```text
assets/files/blog/
```

例如：

```text
assets/files/blog/example-handout.pdf
```

在 blog 正文里放普通链接：

```markdown
[查看 PDF](/assets/files/blog/example-handout.pdf)
```

如果想直接嵌入预览，可以写：

```html
<iframe
  class="blog-pdf-embed"
  src="/assets/files/blog/example-handout.pdf"
  title="Example handout PDF"
></iframe>
```

也可以链接和预览一起放：

```markdown
[查看 PDF](/assets/files/blog/example-handout.pdf)

<iframe
  class="blog-pdf-embed"
  src="/assets/files/blog/example-handout.pdf"
  title="Example handout PDF"
></iframe>
```

文件名仍然建议使用小写英文和连字符，不要使用空格或中文。

## Blog 日期、时区和缓存

当前 `_config.yml` 使用北京时间：

```yml
timezone: Asia/Shanghai
```


如果 push 后线上暂时看不到文章，先检查：

1. GitHub Actions 是否构建成功；
2. 文章是否在 `_posts/` 目录；
3. 文件是否是 `.md` / `.markdown`，且没有生成文件名冲突；
4. front matter 是否从第一行开始；
5. `date` 是否不是未来时间；
6. 浏览器或 GitHub Pages 缓存是否还没刷新。

GitHub Pages 可能缓存几分钟。如果你确认线上 HTML 已经更新，但浏览器还没显示，可以尝试 `Ctrl + F5` 强制刷新，或者用无痕窗口打开。

## 已有分类目录

```text
assets/pdf/algebra/
assets/pdf/commutative-algebra/
assets/pdf/algebraic-geometry/
assets/pdf/representation-theory/
assets/pdf/homological-algebra/
assets/pdf/number-theory/
assets/pdf/analysis/
assets/pdf/misc/
```

可选 TeX 源码目录：

```text
assets/tex/algebra/
assets/tex/commutative-algebra/
assets/tex/algebraic-geometry/
assets/tex/representation-theory/
assets/tex/homological-algebra/
assets/tex/number-theory/
assets/tex/analysis/
assets/tex/misc/
```

旧版目录 `assets/notes/<category>/` 仍然兼容；但之后建议优先使用 `assets/pdf/` 和 `assets/tex/`。

## 文件命名建议

建议使用小写英文和连字符：

```text
sheaves.pdf
schemes.pdf
characters.pdf
orthogonality-relations.pdf
```

PDF 笔记建议使用上述命名，便于分享链接；Blog 支持中文和空格文件名。

## 如何部署到 GitHub Pages

1. 把这个文件夹内容放进你的 GitHub repo。
2. 进入 repo 的 Settings → Pages。
3. Build and deployment 选择 **GitHub Actions**。
4. push 到 `main` 或 `master` 分支。

GitHub Actions 会自动：

1. 在临时构建副本中补全 Blog 配置并自动转换文件名；
2. 检查文章命名、笔记分类、文件格式和发布总体积；
3. 扫描 `assets/pdf/` 下的 `.pdf`；
4. 扫描 `assets/tex/` 下同名 `.tex`，如果存在就附加源码链接；
5. 自动生成 Notes 索引；
6. 构建并检查页面与站内链接；
7. 部署到 GitHub Pages。

因此新增内容时只需要把文件放进正确目录并 push。检查不通过时，发布会在上线前停止，并在 Actions 日志里直接说明是哪一个文件有问题，不会把残缺页面覆盖到线上。

为避免再次出现 Pages 部署超时：

- 单个文件不要超过 95 MB；
- `assets/` 的发布总量不要超过 200 MB；
- `assets/music/` 不会被发布，网站也不会加载音乐播放器。

## 本地预览

安装 Ruby 和 Bundler 后运行：

```bash
bundle install
python3 scripts/generate_notes_data.py
bundle exec jekyll serve
```

然后打开：

```text
http://localhost:4000
```

## 新增分类

假设你想新增 `category-theory`：

1. 新建目录：

```text
assets/pdf/category-theory/
assets/tex/category-theory/
```

2. 在 `_data/categories.yml` 里加入：

```yml
- key: category-theory
  title: Category Theory
  zh: 范畴论
  url: /notes/category-theory/
```

3. 在 `_pages/` 下新增：

```text
_pages/category-theory.md
```

内容：

```markdown
---
layout: category
title: Category Theory
category: category-theory
permalink: /notes/category-theory/
---

Category theory notes.
```

之后就可以上传：

```text
assets/pdf/category-theory/yoneda-lemma.pdf
```

如果想附源码，再上传：

```text
assets/tex/category-theory/yoneda-lemma.tex
```

## 留言与问答（Giscus）

网站的 `/questions/` 页面使用 Giscus，并根据页面地址自动关联 GitHub Discussion。

首次设置：

1. 在仓库 `Settings → General → Features` 中启用 Discussions；
2. 为仓库安装 [Giscus](https://giscus.app/zh-CN)；
3. 将仓库 ID 和 `Q&A` 分类 ID 写入 `_config.yml`：

```yml
giscus:
  repo: "Usami-Renko99/renko06.top"
  repo_id: "R_kgDOTv_0GQ"
  category: "Q&A"
  category_id: "DIC_kwDO..."
```

Giscus 会按 `/questions/` 的页面地址自动匹配讨论，不需要手动创建或填写 Discussion 编号。
