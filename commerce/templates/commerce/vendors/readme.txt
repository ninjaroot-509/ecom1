{% url 'vendpro_detail' pk=product.pk %} ?lien pour les ...


<a href="{% url 'social:begin' 'github' %}">Login with GitHub</a><br>
  <a href="{% url 'social:begin' 'twitter' %}">Login with Twitter</a>
  <a href="{% url 'social:begin' 'facebook' %}">Login with Facebook</a>


  {% if request.user == product.author %}

  {% if product.author == user %}
