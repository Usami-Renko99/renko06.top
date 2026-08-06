---
layout: page
title: Home
---

# 欢迎来到Renko的完美算数教室

这里是我的个人主页。我主要关注数论、表示论、代数几何，也会放一些学习记录和杂谈。

## Main Sections

<div class="grid">
  <a class="tile" href="{{ '/notes/' | relative_url }}">
    <strong>Notes</strong>
    <span>TeX-first 数学笔记归档</span>
  </a>
  <a class="tile" href="{{ '/blog/' | relative_url }}">
    <strong>Blog</strong>
    <span>学习记录与杂谈</span>
  </a>
  <a class="tile" href="{{ '/about/' | relative_url }}">
    <strong>About</strong>
    <span>关于我和这个网站</span>
  </a>
</div>

## Notes Categories

{% for category in site.data.categories %}
- [{{ category.title }} / {{ category.zh }}]({{ category.url | relative_url }})
{% endfor %}
