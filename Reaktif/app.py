from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.form
        
        # Güç ve Tarife
        power_limit = float(data.get('power_limit', 50))
        unit_price = float(data.get('unit_price', 3.45))

        # Çekiş (Tüketim)
        draw_active = float(data.get('draw_active', 0))
        draw_ind = float(data.get('draw_ind', 0))
        draw_cap = float(data.get('draw_cap', 0))

        # Veriş (Üretim)
        feed_active = float(data.get('feed_active', 0))
        feed_uc = float(data.get('feed_uc', 0))   # 6.8.0 Veriş Kapasitif (Cezalı)
        feed_rc = float(data.get('feed_rc', 0))   # 7.8.0 Veriş Endüktif (Muaf)

        # Sınır Oranları (EPDK: 50 kVA altı %33/%20, 50 kVA üstü %20/%15)
        limit_ind_pct = 33.0 if power_limit < 50 else 20.0
        limit_cap_pct = 20.0 if power_limit < 50 else 15.0

        # Çekiş Hesapları
        draw_ind_ratio = (draw_ind / draw_active * 100) if draw_active > 0 else 0
        draw_cap_ratio = (draw_cap / draw_active * 100) if draw_active > 0 else 0

        draw_ind_penalty = draw_ind_ratio > limit_ind_pct
        draw_cap_penalty = draw_cap_ratio > limit_cap_pct

        # Veriş Hesapları
        feed_uc_ratio = (feed_uc / feed_active * 100) if feed_active > 0 else 0
        feed_rc_ratio = (feed_rc / feed_active * 100) if feed_active > 0 else 0

        feed_uc_penalty = feed_uc_ratio > limit_cap_pct
        feed_rc_exempt = True  # 7.8.0 EPDK Mevzuatı gereği muaf (cezasız)

        # TL Ceza Tutar Hesaplama (Yalnızca cezalı kalemler)
        penalty_tl = 0.0
        if draw_ind_penalty: penalty_tl += draw_ind * unit_price
        if draw_cap_penalty: penalty_tl += draw_cap * unit_price
        if feed_uc_penalty:  penalty_tl += feed_uc * unit_price

        result = {
            "status": "success",
            "draw_ind_ratio": round(draw_ind_ratio, 2),
            "draw_cap_ratio": round(draw_cap_ratio, 2),
            "feed_uc_ratio": round(feed_uc_ratio, 2),
            "feed_rc_ratio": round(feed_rc_ratio, 2),
            "limit_ind_pct": limit_ind_pct,
            "limit_cap_pct": limit_cap_pct,
            "draw_ind_penalty": draw_ind_penalty,
            "draw_cap_penalty": draw_cap_penalty,
            "feed_uc_penalty": feed_uc_penalty,
            "feed_rc_exempt": feed_rc_exempt,
            "total_penalty_tl": round(penalty_tl, 2)
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)