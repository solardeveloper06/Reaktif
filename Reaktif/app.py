import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
  result = None
  if request.method == 'POST':
    try:
      active_kwh = float(request.form.get('active_kwh', 0))
      inductive_kvarh = float(request.form.get('inductive_kvarh', 0))
      capacitive_kvarh = float(request.form.get('capacitive_kvarh', 0))

      if active_kwh > 0:
        ind_ratio = (inductive_kvarh / active_kwh) * 100
        cap_ratio = (capacitive_kvarh / active_kwh) * 100
      else:
        ind_ratio = 0
        cap_ratio = 0

      # Standart Ticarethane/Sanayi Sınırları (%20 Endüktif, %15 Kapasitif)
      ind_penalty = ind_ratio > 20
      cap_penalty = cap_ratio > 15

      result = {
          'active': active_kwh,
          'inductive': inductive_kvarh,
          'capacitive': capacitive_kvarh,
          'ind_ratio': round(ind_ratio, 2),
          'cap_ratio': round(cap_ratio, 2),
          'ind_penalty': ind_penalty,
          'cap_penalty': cap_penalty,
          'has_penalty': ind_penalty or cap_penalty,
      }
    except ValueError:
      result = {'error': 'Lütfen geçerli sayısal değerler giriniz.'}

  return render_template('index.html', result=result)


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
