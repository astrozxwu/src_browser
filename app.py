import json
import os

import numpy as np
import pandas as pd
from flask import (Flask, Response, make_response, render_template, request,
                   send_from_directory)
from flask_sqlalchemy import SQLAlchemy

import config
import fit
import tableproc as tp
import vis

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{config.db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Src(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    for i in tp.keys:
        exec("{} = db.Column('{}')".format(i, i))

    def to_dict(self):
        dic = {"id": self.id}
        for i in tp.keys:
            # if i not in ['link', 'tmass']:
            dic[i] = getattr(self, i)
        return dic


global lll
lll = len(Src.query.all())


@app.route("/")
def srclist():
    data = db.engine.execute("SELECT * FROM Src where Status = 1;")
    Events = [i["Event"] for i in data]
    mdtime = fit.getmdtime(Events)
    data = db.engine.execute("SELECT * FROM Src where Status = 1;")
    return render_template(
        "srclist.html",
        data=data,
        tags=config.key_tags + list(config.map_tags.keys()) + config.idle_tags,
        mdtime=mdtime,
    )


@app.route("/download", methods=["POST"])
def download():
    sql = "SELECT * FROM Src"
    idx = request.form["indexes"][1:-1]
    if idx:
        sql += f" WHERE ID IN ({idx})"
    data = db.engine.execute(sql)
    df = pd.DataFrame(data, columns=["id"] + tp.keys)[tp.keys].to_csv(index=False)
    # resp = make_response(df)
    # cd = "attachment; filename=mycsv.csv"
    # resp.headers["Content-Disposition"] = cd
    # resp.headers["Cache-Control"] = "must-revalidate"
    # resp.headers["Pragma"] = "must-revalidate"
    # resp.headers["Content-type"] = "application/csv"
    # resp.mimetype = "text/csv"
    # return resp
    return Response(df, mimetype="text/csv")


@app.route("/query", methods=["POST"])
def query():
    query = request.form["query"]
    sql = "SELECT * FROM Src"
    idx = request.form["indexes"][1:-1]
    if query:
        sql = sql + " WHERE " + query
    if idx:
        sql += f" AND ID IN ({idx})"
    words = sql.split()
    ind = np.where(np.array(words) == "like")[0]
    for i in ind:
        words[i + 1] = "'%{}%'".format(words[i + 1])
    sql = " ".join(words)
    print(query)
    data = db.engine.execute(sql)
    Events = [i["Event"] for i in data]
    mdtime = fit.getmdtime(Events)
    data = db.engine.execute(sql)
    return render_template("table.html", data=data, mdtime=mdtime)


@app.route("/update", methods=["POST"])
def update():
    pk = request.form["pk"]
    name = request.form["name"]
    value = request.form["value"]
    # print(pk,name,value)
    if name in ["Can", "Status", "Comment", "t0", "tE", "Kmag", "r_K"]:
        if not value:
            value = "-1"
        if name == "Comment":
            value = f"'{value}'"
        db.engine.execute(
            "UPDATE Src SET {} = {} WHERE id = {} ".format(name, value, pk)
        )
        db.session.commit()
    return json.dumps({"status": "OK"})


@app.route("/src/<Event>")
def src(Event, chartID="chart_ID"):
    # if auth.jwtVerify(request.cookies):
    query = Src.query.filter(Src.Event.ilike(f"%{Event}%"))
    x = query[0].to_dict()
    event_name = x["Event"]
    id = x["id"]
    id_prev = id - 1 * (id is not 0)
    id_next = id + 1 * (id is not (lll - 1))
    prev = Src.query.filter(Src.id.ilike(f"%{id_prev}%"))[0].to_dict()["Event"]
    next = Src.query.filter(Src.id.ilike(f"%{id_next}%"))[0].to_dict()["Event"]
    pageType = "graph"
    chart = {"renderTo": chartID, "zoomType": "xy", "height": "100%"}
    series = fit.getdata(event_name)
    title = {"text": event_name}
    pars, models = fit.loadfit(event_name)
    key_tg = {i: 1 * (x[i] > 0) for i in config.key_tags}
    idle_tg = {i: 1 * (i in x["Tags"]) for i in config.idle_tags}
    map_tg = {i: 1 * (x[config.map_tags[i]] > 0) for i in config.map_tags.keys()}
    tg = {**key_tg, **idle_tg, **map_tg}
    v = vis.load_vlti_vis(os.path.join(config.data_path, event_name, 'vlti_vis.csv'))
    return render_template(
        "src.html",
        pageType=pageType,
        chartID=chartID,
        chart=chart,
        series=series,
        title=title,
        src=x,
        pars=pars,
        models=models,
        fit_info="success",
        tags=tg,
        prev=prev,
        next=next,
        vlti_vis=v
    )


@app.route("/renew_vis", methods=["POST"])
def renew_vis():
    event = str(request.form.get("event_name"))
    RA = str(request.form.get("RA"))
    Dec = str(request.form.get("Dec"))
    ra_dec = RA + " " + Dec
    output = os.path.join(config.data_path, event, "vis.png")
    _, v = vis.gen_vis_fig(ra_dec, output=output)
    pk = request.form.get("pk")
    query = Src.query.filter(Src.id.ilike(f"%{pk}%"))
    x = query[0].to_dict()["Tags"]
    print(x)
    if v and "Visible;" not in x:
        x += "Visible;"
        db.engine.execute(
            "UPDATE Src SET {} = '{}' WHERE id = {} ".format("Tags", x, pk)
        )
    elif not v and "Visible;" in x:
        x.replace("Visible;", "")
        db.engine.execute(
            "UPDATE Src SET {} = '{}' WHERE id = {} ".format("Tags", x, pk)
        )

    return f"""<img style='height: 100%; width: 100%; object-fit: contain'
    src="../data/{event}/vis.png">"""


@app.route("/vlti_vis", methods=["POST"])
def vlti_vis():
    event = str(request.form.get("event_name"))
    RA = str(request.form.get("RA"))
    Dec = str(request.form.get("Dec"))
    ra_dec = RA + " " + Dec
    output = os.path.join(config.data_path, event, "vlti_vis.csv")
    v = vis.vlti_vis(ra_dec, output=output)
    v = vis.gen_vis_fig(ra_dec, output=output)
    return render_template("vlti_vis.html", vlti_vis = v) 





@app.route("/fitparm", methods=["POST"])
def fitparm():
    u0 = float(request.form.get("u0"))
    bl = float(request.form.get("bl"))
    t0 = request.form.get("t0")
    tE = request.form.get("tE")

    t0 = 9750.0 if t0 == "None" else float(t0)
    tE = 50.0 if tE == "None" else float(tE)
    event_name = request.form.get("event_name")
    fit_info = fit.fit(event_name, u_0=u0, t_0=t0, t_E=tE, bl=int(bl))
    print(u0, bl, t0, tE, fit_info)
    pars, models = fit.loadfit(event_name)
    return render_template("fitform.html", pars=pars, models=models, fit_info=fit_info)


@app.route("/updatetags", methods=["POST"])
def updatetags():
    tag = request.form.get("tag") + ";"
    checked = request.form.get("checked") == "true"
    pk = request.form.get("pk")
    query = Src.query.filter(Src.id.ilike(f"%{pk}%"))
    x = query[0].to_dict()["Tags"]
    if not checked:
        if tag[:-1] in config.idle_tags:
            x = x.replace(tag, "")
            db.engine.execute(
                "UPDATE Src SET {} = '{}' WHERE id = {} ".format("Tags", x, pk)
            )
        if tag[:-1] in config.key_tags:
            db.engine.execute(
                "UPDATE Src SET {} = 0 WHERE id = {} ".format(tag[:-1], pk)
            )
        if tag[:-1] in config.map_tags.keys():
            real_key = config.map_tags.keys()[tag[:-1]]
            db.engine.execute(
                "UPDATE Src SET {} = 0 WHERE id = {} ".format(real_key, pk)
            )
    else:
        if tag[:-1] in config.idle_tags:
            x += tag
            db.engine.execute(
                "UPDATE Src SET {} = '{}' WHERE id = {} ".format("Tags", x, pk)
            )
        if tag[:-1] in config.map_tags.keys():
            real_key = config.map_tags.keys()[tag[:-1]]
            db.engine.execute(
                "UPDATE Src SET {} = 1 WHERE id = {} ".format(real_key, pk)
            )
        if tag[:-1] in config.key_tags:
            db.engine.execute(
                "UPDATE Src SET {} = 1 WHERE id = {} ".format(tag[:-1], pk)
            )
    return json.dumps({"status": "OK"})


def h2d(ra, dec):
    sgn = 1
    if "-" in dec:
        sgn = -1
    dec = dec.replace("-", "")
    a, b, c = [float(i) for i in ra.split(":")]
    d, e, f = [float(i) for i in dec.split(":")]
    alpha = (a + b / 60 + c / 3600) * 15
    delta = sgn * (d + e / 60 + f / 3600)
    return alpha, delta


def lb(ra, dec):
    ra_dec = ra + " " + dec
    return tp.get_lb(ra_dec)


app.jinja_env.globals.update(h2d=h2d)
app.jinja_env.globals.update(zip=zip)
app.jinja_env.globals.update(lb=lb)


@app.route("/data/<path:path>")
def send_report(path):
    return send_from_directory("data", path)


if __name__ == "__main__":
    app.run()
