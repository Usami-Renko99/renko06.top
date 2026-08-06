---
layout: page
title: Blog
permalink: /blog/
---

{% if site.posts.size > 0 %}
  <div class="post-list">
    {% for post in site.posts %}
      <article class="post-card">
        {% if post.cover %}
          {% assign cover_file = site.static_files | where: "path", post.cover | first %}
        {% endif %}
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
          <p class="meta">{{ post.date | date: "%Y-%m-%d" }}</p>
          {% if post.excerpt %}
            <p class="post-excerpt">{{ post.excerpt | strip_html | truncate: 120 }}</p>
          {% endif %}
        </div>
      </article>
    {% endfor %}
  </div>
{% else %}
  <p>暂时还没有文章。</p>
{% endif %}
