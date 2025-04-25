# Informe Final de Análisis Financiero

**Fecha de generación:** {{ fecha }}

---

## Estado inicial del portafolio

{{ portafolio_inicial }}

---

## Noticias utilizadas

{% if urls %}
{% for url in urls %}
- {{ url }}
{% endfor %}
{% else %}
_No se encontraron noticias referenciadas._
{% endif %}

---

## Propuesta de redistribución

{% if redistribucion %}
{{ redistribucion }}
{% else %}
_No se generó ninguna propuesta._
{% endif %}

---

## Decisión final

{{ decision }}

---

_FinsightAI - Asistente Inteligente de Análisis Financiero_
