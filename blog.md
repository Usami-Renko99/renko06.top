---
layout: page
title: Blog
display_title: 记录与杂谈
eyebrow: JOURNAL
permalink: /blog/
---

{% if site.posts.size > 0 %}
  <div class="post-list">
    {% for post in site.posts %}
      {% assign cover_file = nil %}
      {% if post.cover %}
        {% assign cover_file = site.static_files | where: "path", post.cover | first %}
      {% endif %}
      <article class="post-card{% unless post.cover and cover_file %} post-card-no-cover{% endunless %}">
        {% if post.cover and cover_file %}
          <a class="post-card-cover" href="{{ post.url | relative_url }}" aria-label="{{ post.title | escape }}">
            <img
              src="{{ post.cover | relative_url }}"
              alt="{{ post.cover_alt | default: post.title | escape }}"
              loading="lazy"
            >
          </a>
        {% endif %}
        <div class="post-card-body">
          <h2 class="post-card-title">
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
          </h2>
          <p class="meta"><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y.%m.%d" }}</time></p>
          {% if post.excerpt %}
            <p class="post-excerpt">{{ post.excerpt | strip_html | truncate: 120 }}</p>
          {% endif %}
          <a class="text-link" href="{{ post.url | relative_url }}" aria-label="阅读 {{ post.title | escape }}">阅读全文 <span aria-hidden="true">↗</span></a>
        </div>
      </article>
    {% endfor %}
  </div>
{% else %}
  <div class="empty-state"><p>还没有发表文章，新的记录会在这里相见。</p></div>
{% endif %}
