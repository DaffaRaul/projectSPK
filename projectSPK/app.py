from flask import Flask, render_template, request, redirect, url_for, session, send_file
import openpyxl, io

app = Flask(__name__)
app.secret_key = 'rahasia'

# Data dummy
items = [
    {'id':1, 'nama':'Kaos A', 'harga':50000, 'stok':100, 'rating':4.5},
    {'id':2, 'nama':'Kemeja B', 'harga':75000, 'stok':50, 'rating':4.0},
]

def saw(data, weights, benefit):
    norm = {}
    for crit in weights:
        vals = [d[crit] for d in data]
        if benefit[crit]:
            norma = [v/max(vals) for v in vals]
        else:
            norma = [min(vals)/v for v in vals]
        norm[crit] = norma
    results = []
    for i,d in enumerate(data):
        score = sum(norm[crit][i]*weights[crit] for crit in weights)
        results.append({'id':d['id'],'nama':d['nama'],'score':score})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        if request.form['username']=='admin' and request.form['password']=='admin':
            session['user']='admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Login gagal')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', items=items)

@app.route('/item/<action>', methods=['POST'])
def item_action(action):
    if 'user' not in session: return redirect(url_for('login'))
    nama = request.form['nama']; harga=int(request.form['harga'])
    stok=int(request.form['stok']); rating=float(request.form['rating'])
    if action=='add':
        nid = max(i['id'] for i in items)+1 if items else 1
        items.append({'id':nid,'nama':nama,'harga':harga,'stok':stok,'rating':rating})
    elif action=='edit':
        idx = next(i for i in items if i['id']==int(request.form['id']))
        idx.update({'nama':nama,'harga':harga,'stok':stok,'rating':rating})
    elif action=='delete':
        items[:] = [i for i in items if i['id']!=int(request.form['id'])]
    return redirect(url_for('dashboard'))

@app.route('/nilai')
def nilai():
    if 'user' not in session: return redirect(url_for('login'))
    w = {'harga':0.4, 'stok':0.3, 'rating':0.3}
    benefit = {'harga':False, 'stok':True, 'rating':True}
    res = saw(items, w, benefit)
    return render_template('hasil.html', hasil=res)

@app.route('/export')
def export():
    if 'user' not in session: return redirect(url_for('login'))
    w = {'harga':0.4, 'stok':0.3, 'rating':0.3}
    benefit = {'harga':False, 'stok':True, 'rating':True}
    res = saw(items, w, benefit)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['ID','Nama','Score'])
    for r in res:
        ws.append([r['id'], r['nama'], r['score']])
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)

    return send_file(buf,
                     download_name="hasil_saw.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__=='__main__':
    app.run(debug=True)