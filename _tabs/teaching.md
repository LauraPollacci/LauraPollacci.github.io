---
layout: page
title: Teaching
icon: fas fa-chalkboard-teacher
order: 3
permalink: /tabs/teaching/
---

Below is a selection of courses I've taught. Click a course to open its page.

{% assign groups = site.teaching | group_by: "year" | sort: "name" | reverse %}
{% if groups and groups.size > 0 %}
  {% for g in groups %}
  <h2>{{ g.name }}</h2>
  <ul>
    {% assign items = g.items | sort: "title" %}
    {% for c in items %}
      <li>
        <a href="{{ c.url | relative_url }}">{{ c.title }}</a>
        {% if c.term %} — <em>{{ c.term }}</em>{% endif %}
        {% if c.level %} • {{ c.level }}{% endif %}
      </li>
    {% endfor %}
  </ul>
  {% endfor %}
{% else %}
  <p><em>No courses found (site.teaching is empty).</em></p>
{% endif %}
